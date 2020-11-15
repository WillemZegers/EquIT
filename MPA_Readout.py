#!/usr/bin/env python3

########################################################################################################################
# Project: Equine Wearable Device (EWD)
# Author: Willem Zegers
# GitHub: https://github.com/WillemZegers
# Date Created: 2020/11/12
# Purpose: Code that will acquire data from Shimmer3.
########################################################################################################################


from bluetooth import *
import struct
import sys
import time



class MPA_Sensor_Readout(object):
    def __init__(self):

        print('STARTING APPLICATION')

        # Declare variables
        self.nearby_devices = []
        self.numbytes = 0
        self.ddata = bytearray()

        # Search for a nearby Shimmer
        self.scan_for_bluetooth_devices()

        # Once a shimmer is found, read samples
        self.RUN = True

        # Once a connection is made, receive data
        while self.RUN:
            self.read_shimmer_measurements()


    def wait_for_ack(self):
        """
        Class to handle Shimmer acknowledge
        """
        ddata = ""
        ack = struct.pack('B', 0xff)
        while ddata != ack:
            ddata = self.bt_sock.recv(1)
        return


    def setup_shimmer_connection(self, Shimmer_Mac):
        """
        Class to configure the Shimmer for streaming
        """

        try:
            # Setup Bluetooth socket
            self.bt_sock = BluetoothSocket( RFCOMM )
            self.bt_sock.connect((Shimmer_Mac, 1))
            print('CONNECTED TO DEVICE WITH MAC ' + str(Shimmer_Mac))

            # Set desired sensor
            self.bt_sock.send(struct.pack('BBBB', 0x08, 0x80, 0x00, 0x00))  # analogaccel
            self.wait_for_ack()
            print('CONFIGURED SENSOR TYPE FOR ACCEL')

            # Set sampling rate
            self.bt_sock.send(struct.pack('BBB', 0x05, 0x00, 0x19)) #5.12Hz (6400 (0x1900)). Has to be done like this for alignment reasons
            self.wait_for_ack()
            print('CONFIGURED SENSOR TYPE FOR ACCEL')

            # send start streaming command
            self.bt_sock.send(struct.pack('B', 0x07))
            self.wait_for_ack()
            print('STARTED STREAMING')

            # Set frame size
            self.framesize = 10  # 1byte packet type + 3byte timestamp + 3x2byte Analog Accel


        except BluetoothError as error:
            # When no connection can be made with the device
            print("Could not connect: ", error, "")
            self.bt_sock.close()
            self.nearby_devices = []
            return False

        except:
            # Show the user that there is a problem
            print('', sys.exc_info()[1])
            self.nearby_devices = []
            return False


    def scan_for_bluetooth_devices(self):
        """
        Class to look for nearby shimmers
        """
        print('SEARCHING FOR BLUETOOTH DEVICES')

        try:
            while not self.nearby_devices:

                # Start looking for shimmers
                self.nearby_devices = discover_devices(lookup_names=True, flush_cache=True)

                # When there are devices found
                if self.nearby_devices:

                    print('FOUND: ' + str(len(self.nearby_devices)) + ' BLUETOOTH DEVICES')

                    for addr, name in self.nearby_devices:
                        print(str(addr), str(name))

                    # Configure the Shimmer to read ECG values
                    print('CONNECTING TO DEVICE WITH MAC ' + str(addr))

                    if self.setup_shimmer_connection(addr):
                        # If setup was successful, stop scanning
                        break
                    else:
                        # If setup was not successful, continue scanning
                        pass

                else:
                    # If no devices are found, wait for a while and retry
                    print('NO SHIMMER FOUND, RETRYING IN 5SEC ...')
                    time.sleep(5)

        except KeyboardInterrupt:
            self.close_application()


    def read_shimmer_measurements(self):
        """
        Class to stream Shimmer data endlessly
        """

        # Read a chunk of data from the shimmer
        try:

            while self.numbytes < self.framesize:
                self.ddata += self.bt_sock.recv(self.framesize)
                self.numbytes = len(self.ddata)

            data = self.ddata[0:self.framesize]
            self.ddata = self.ddata[self.framesize:]
            self.numbytes = len(self.ddata)

            # Start unpacking data
            (timestamp0, timestamp1, timestamp2) = struct.unpack('BBB', data[1:4])
            (analogaccelx, analogaccely, analogaccelz) = struct.unpack('HHH', data[4:self.framesize])
            timestamp = timestamp0 + timestamp1 * 256 + timestamp2 * 65536
            timestamp = timestamp0 + timestamp1 * 256 + timestamp2 * 65536

            try:
                # TODO Process data
                print('ACCEL VALUES: ', str(timestamp), ' : ', str(analogaccelx), ' - ', str(analogaccely), ' - ', str(analogaccelz))

            except:
                print('DATA FORMAT ERROR')

        except KeyboardInterrupt:
            self.close_application()

        except:
            # Show the user that there is a problem
            print('SHIMMER READING ERROR')
            print('', sys.exc_info()[1])
            self.close_application()


    def close_application(self):
        """
        Routine to terminate all processes and exit.
        """
        # Stop the management thread
        self.RUN = False

        # Say goodbye to the viewers
        print('Closing application')

        # Kill the program
        sys.exit()


if __name__ == "__main__":

    # Start the program on the specified port
    MPA_Sensor_Readout()