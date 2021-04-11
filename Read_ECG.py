import numpy
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication

class Read_ECG():

    def __init__(self, parent=None):

        # Start
        self.show_signal()

    def show_signal(self):
        try:
            # Reconstruct the filepath
            file_path = "C:\\Users\\Willem\\PycharmProjects\\horse-monitor-ecg\\EWD Server\\RECORDINGS\\21-03-16_19-51-49.ecg"

            # Get file version number
            f = open(file_path, "r")
            vesion_number = f.readline().split(' ')[1].rstrip()
            text = f.readline()

            if vesion_number == "0.1.0":

                # Load the data
                recording = f.readline().rstrip()
                recording = recording.split('#')

                # Create some variables to store data
                ECG_Data_v1 = []
                ECG_Data_v2 = []
                ECG_Data_t = []

                if len(recording) > 0:
                    # Remove last item
                    recording = recording[:-1]

                    # Break up data in records
                    for record in recording:
                        # Break up records in fields
                        fields = record.split(':')

                        # Obtain the fields
                        ECG_Data_v1.append(fields[0].split(','))
                        ECG_Data_v2.append(fields[1].split(','))
                        ECG_Data_t.append(fields[2].split(','))

                    # Flatten lists
                    flat_ECG_Data_v1 = [item for sublist in ECG_Data_v1 for item in sublist]
                    flat_ECG_Data_v2 = [item for sublist in ECG_Data_v2 for item in sublist]
                    flat_ECG_Data_t = [item for sublist in ECG_Data_t for item in sublist]

                    # Covert to np array
                    V1 = numpy.asarray(flat_ECG_Data_v1, dtype=int)
                    V2 = numpy.asarray(flat_ECG_Data_v2, dtype=int)

                    # Close the file
                    f.close()

                    # Plot results
                    pg.plot(V1)
                    pg.plot(V2)


                else:
                    # If the file is empty
                    f.close()
                    print("The selected .ECG file is empty.")

            else:
                # If the version number is unknown
                f.close()
                print("The selected .ECG file has an old (unsupported) version.")

        except:
            print('Some error occurred:')
            print('' + sys.exc_info()[1])


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    main_app = Read_ECG()

    sys.exit(app.exec_())