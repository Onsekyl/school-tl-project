/*
 * Copyright (c) 2023 Nordic Semiconductor ASA
 *
 * SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
 */

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gap.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/bluetooth/conn.h>
#include <dk_buttons_and_leds.h>
#include <string.h>
#include "my_lbs.h"
#include "adc.h"

static const struct bt_le_adv_param *adv_param = BT_LE_ADV_PARAM(
	(BT_LE_ADV_OPT_CONN |
	 BT_LE_ADV_OPT_USE_IDENTITY), /* Connectable advertising and use identity address */
	800, /* Min Advertising Interval 500ms (800*0.625ms) */
	801, /* Max Advertising Interval 500.625ms (801*0.625ms) */
	NULL); /* Set to NULL for undirected advertising */

LOG_MODULE_REGISTER(Lesson4_Exercise2, LOG_LEVEL_INF);

#define DEVICE_NAME CONFIG_BT_DEVICE_NAME
#define DEVICE_NAME_LEN (sizeof(DEVICE_NAME) - 1)

#define RUN_STATUS_LED DK_LED1
#define CON_STATUS_LED DK_LED2
#define USER_LED DK_LED3
#define USER_BUTTON DK_BTN1_MSK
#define DIR_BUTTON DK_BTN2_MSK
#define BURST_BUTTON DK_BTN3_MSK

#define STACKSIZE 1024
#define PRIORITY 7

#define RUN_LED_BLINK_INTERVAL 1000
#define BURST_POLL_INTERVAL 250
static bool app_button_state;
static struct k_work adv_work;

uint16_t dir = 0;

#define BURST_MEASUREMENTS 100
bool burst_measure = false;

/* STEP 15 - Define the data you want to stream over Bluetooth LE */
static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),

};

static const struct bt_data sd[] = {
	BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_LBS_VAL),
};

static void adv_work_handler(struct k_work *work)
{
	int err = bt_le_adv_start(adv_param, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));

	if (err) {
		printk("Advertising failed to start (err %d)\n", err);
		return;
	}

	printk("Advertising successfully started\n");
}
static void advertising_start(void)
{
	k_work_submit(&adv_work);
}
static void recycled_cb(void)
{
	printk("Connection object available from previous conn. Disconnect is complete!\n");
	advertising_start();
}

static void app_led_cb(bool led_state)
{
	dk_set_led(USER_LED, led_state);
}

static bool app_button_cb(void)
{
	return app_button_state;
}

// Moving this inside send_data_thread creates a stack overflow
struct Measurement measurements[BURST_MEASUREMENTS];

// Polls burst_measure periodically
void send_data_thread(void)
{
	while (1)
	{
		if (burst_measure)
		{
			/* Timestamps shows that 100 measurements took about
			 * 0.02225 s -> (1/0.02225) * 100 = 4494, so is
			 * possible measurements in one second about 4400? */
			// LOG_INF("Starting measurements");
			for (int i = 0; i < BURST_MEASUREMENTS; i++)
			{
				measurements[i] = readADCValue();
			}
			// LOG_INF("Measurements done");

			for (int i = 0; i < BURST_MEASUREMENTS; i++)
			{
				// printk("ADC reading #%d: x: %d, y: %d, z: %d, dir: %d\n", i + 1, measurements[i].x, measurements[i].y, measurements[i].z, dir);
				int err = my_lbs_send_sensor_notify(measurements[i].x, measurements[i].y, measurements[i].z, dir);
				if (err < 0)
				{
					printk("\tFailed to send burst measurement: %d (index %d)\n", err, i);
					break;
				}
			}
			
			burst_measure = false;
			printk("\tBurst measurement and send finished\n");
		}

		k_sleep(K_MSEC(BURST_POLL_INTERVAL));
	}
	// while (1) {
	// 	accelerometer = readADCValue();
	// 	// printk("ADC reading: x: %d, y: %d, z: %d\n", accelerometer.x, accelerometer.y, accelerometer.z);
	// 	/* Send notification, the function sends notifications only if a client is subscribed */
	// 	my_lbs_send_sensor_notify(accelerometer.x, accelerometer.y, accelerometer.z , dir);
	// 	k_sleep(K_MSEC(NOTIFY_INTERVAL));
	// }
}

static struct my_lbs_cb app_callbacks = {
	.led_cb = app_led_cb,
	.button_cb = app_button_cb,
};

char direction_name[6][8] = {"x down", "x up", "y down", "y up", "z down", "z up"};
static void button_changed(uint32_t button_state, uint32_t has_changed)
{
	// printk("button_changed called with state: %d and has_changed: %d\n", button_state, has_changed);

	if (has_changed & DIR_BUTTON) {
		uint32_t dir_button_state = button_state & DIR_BUTTON;

		if (dir_button_state)
		{
			dir = (dir >= 5) ? 0 : ++dir;
			printk("DIR_BUTTON pressed, direction changed to: %d -> %s\n", dir, direction_name[dir]);
		}

		/* STEP 6 - Send indication on a button press */
		my_lbs_send_button_state_indicate(dir_button_state);
		app_button_state = dir_button_state ? true : false;
	}
	else if (has_changed & BURST_BUTTON) {
		uint32_t burst_button_state = button_state & BURST_BUTTON;

		if (burst_button_state && !burst_measure)
		{
			burst_measure = true;
			printk("BURST_BUTTON pressed, performing and sending %d accelerometer"
				   " measurements to subscribers...\n", BURST_MEASUREMENTS);
		}
	}
}
static void on_connected(struct bt_conn *conn, uint8_t err)
{
	if (err) {
		printk("Connection failed (err %u)\n", err);
		return;
	}

	printk("Connected\n");

	dk_set_led_on(CON_STATUS_LED);
}

static void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
	printk("Disconnected (reason %u)\n", reason);

	dk_set_led_off(CON_STATUS_LED);
}

struct bt_conn_cb connection_callbacks = {
	.connected = on_connected,
	.disconnected = on_disconnected,
	.recycled = recycled_cb,
};

static int init_button(void)
{
	int err;

	err = dk_buttons_init(button_changed);
	if (err) {
		printk("Cannot init buttons (err: %d)\n", err);
	}

	return err;
}

int main(void)
{
	int blink_status = 0;
	int err;

	LOG_INF("Starting Lesson 4 - Exercise 2 \n");

	err = dk_leds_init();
	if (err) {
		LOG_ERR("LEDs init failed (err %d)\n", err);
		return -1;
	}

	err = init_button();
	if (err) {
		printk("Button init failed (err %d)\n", err);
		return -1;
	}

	initializeADC();

	err = bt_enable(NULL);
	if (err) {
		LOG_ERR("Bluetooth init failed (err %d)\n", err);
		return -1;
	}
	bt_conn_cb_register(&connection_callbacks);

	err = my_lbs_init(&app_callbacks);
	if (err) {
		printk("Failed to init LBS (err:%d)\n", err);
		return -1;
	}
	LOG_INF("Bluetooth initialized\n");
	k_work_init(&adv_work, adv_work_handler);
	advertising_start();
	for (;;) {
		dk_set_led(RUN_STATUS_LED, (++blink_status) % 2);
		k_sleep(K_MSEC(RUN_LED_BLINK_INTERVAL));
	}
}
/* STEP 18.2 - Define and initialize a thread to send data periodically */
K_THREAD_DEFINE(send_data_thread_id, STACKSIZE, send_data_thread, NULL, NULL, NULL, PRIORITY, 0, 0);
