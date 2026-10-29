/*
 * https://www.youtube.com/watch?v=Lcjt2Iu2xvY
 */

#include <stdio.h>
#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/adc.h>

#define SLEEP_TIME_MS 1000

#define ADC_NODE DT_NODELABEL(adc)
static const struct device *adc_dev = DEVICE_DT_GET(ADC_NODE);

#define ADC_RESOLUTION 10
#define ADC_CHANNEL 0
#define ADC_PORT SAADC_CH_PSELN_PSELN_AnalogInput0
#define ADC_REFERENCE ADC_REF_INTERNAL
#define ADC_GAIN ADC_GAIN_1_5


struct adc_channel_cfg ch0_cfg = {
	.gain = ADC_GAIN,
	.reference = ADC_REFERENCE,
	.acquisition_time = ADC_ACQ_TIME_DEFAULT,
	.channel_id = ADC_CHANNEL,
#ifdef CONFIG_ADC_NRFX_SAADC
	.input_positive = ADC_PORT
#endif
};

int16_t sample_buffer[1];
struct adc_sequence sequence = {
	.channels = BIT(ADC_CHANNEL),
	.buffer = sample_buffer,
	.buffer_size = sizeof(sample_buffer),
	.resolution = ADC_RESOLUTION
};


int main(void)
{
	int ret;

	if (!device_is_ready(adc_dev))
	{
		printk("adc_dev not ready\n");
		return 0;
	}

	ret = adc_channel_setup(adc_dev, &ch0_cfg);
	if (ret != 0)
	{
		printk("ADC adc_channel_setup failed with error: %d.\n", ret);
		return 0;
	}

	while (1)
	{
		ret = adc_read(adc_dev, &sequence);
		if (ret != 0)
		{
			printk("ADC reading failed with error %d.\n", ret);
			return 0;
		}

		int32_t mv_value = sample_buffer[0];
		// printk("ADC-value: %d\n", mv_value);

		int32_t adc_vref = adc_ref_internal(adc_dev);
		adc_raw_to_millivolts(adc_vref, ADC_GAIN, ADC_RESOLUTION, &mv_value);
		printk("Y-axis voltage: %d mV\n", mv_value);

		k_msleep(SLEEP_TIME_MS);
	}
	return 0;
}
