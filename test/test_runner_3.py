from jumper.vlab import Vlab
import unittest
import setting
import boto3
import json
import os


client = boto3.client('iot-data',
                      region_name='us-east-1',
                      aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
                      )


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        print(self.id().split('.')[-1])  # test name
        self.vlab = Vlab(working_directory=setting.dir, print_uart=True)
        self.vlab.load(setting.fw_bin_aws)
        self.uart = self.vlab.uart
        self.vlab.run_for_ms(500)
        print('Virtual device is running')

    def tearDown(self):
        self.vlab.stop()

    def push_button(self):
        print('Button on')
        self.vlab.BUTTON1.on()
        self.vlab.run_for_ms(60)
        print('Button off')
        self.vlab.BUTTON1.off()
        self.vlab.run_for_ms(600)

    def read_from_aws(self):
        response = client.get_thing_shadow(thingName='TemperatureSensor')
        streaming_body = response["payload"]
        raw_data_bytes = streaming_body.read()
        raw_data_string = raw_data_bytes.decode('utf-8')  # Python 3.x specific
        json_state = json.loads(raw_data_string)
        return json_state['state']['desired']['temprature']

    '''
    Integration Test
    Set temperature, click a button and verify that the shadow device on AWS was updated with the same temperature
    '''
    def test_3_Integration_Test(self):
        for i in range(20):
            self.push_button()
            temp = int(self.read_from_aws())
            print('temperature is ' + str(temp))
            self.assertTrue(20 <= temp <= 40)


if __name__ == '__main__':
    unittest.main()
