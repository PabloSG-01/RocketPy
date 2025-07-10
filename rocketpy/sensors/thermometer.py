import numpy as np

from ..mathutils.vector_matrix import Matrix
from ..prints.sensors_prints import _SensorPrints
from ..sensors.sensor import ScalarSensor

class Thermometer(ScalarSensor):
    """Class for the thermometer sensor"""

    units = "ºC"

    def __init__(
        self,
        sampling_rate,
        measurement_range=np.inf,
        resolution=0,
        noise_density=0,
        noise_variance=1,
        random_walk_density=0,
        random_walk_variance=1,
        constant_bias=0,
        name="Thermometer",
    ):
        """
        Initialize the thermometer sensor.

        Parameters
        ----------
        sampling_rate : float
            Sample rate of the sensor in Hz.
        measurement_range : float or tuple, optional
            Measurement range in °C or K. Default is np.inf.
        resolution : float, optional
            Resolution of the sensor in °C/LSB. Default is 0 (no quantization).
        noise_density : float, optional
            White noise density in °C/√Hz. Default is 0.
        noise_variance : float, optional
            Noise variance in °C². Default is 1.
        random_walk_density : float, optional
            Random walk density in °C/√Hz. Default is 0.
        random_walk_variance : float, optional
            Random walk variance in °C². Default is 1.
        constant_bias : float, optional
            Constant sensor bias in °C. Default is 0.
        name : str, optional
            Sensor name. Default is "Thermometer".
        """
        super().__init__(
            sampling_rate=sampling_rate,
            measurement_range=measurement_range,
            resolution=resolution,
            noise_density=noise_density,
            noise_variance=noise_variance,
            random_walk_density=random_walk_density,
            random_walk_variance=random_walk_variance,
            constant_bias=constant_bias,    
            operating_temperature=298.15,  # No efecto térmico adicional
            temperature_bias=0,
            temperature_scale_factor=0,
            name=name,
        )
        self.prints = _SensorPrints(self)

    def measure(self, time, **kwargs):
        """
        Measures temperature at a given location.

        Parameters
        ----------
        time : float
            Current time in seconds.
        kwargs : dict
            Dictionary with the following key:
            - environment : Environment
                Environment object containing atmospheric conditions.

        Returns
        -------
        None
        """

        u = kwargs["u"]
        relative_position = kwargs["relative_position"]
        temperature = kwargs["environment"].temperature # ideal temperature at sensor location

        # Calculate the altitude of the sensor
        relative_altitude = (Matrix.transformation(u[6:10]) @ relative_position).z

        # Calculate the pressure at the sensor location and add noise
        Temp = temperature(relative_altitude + u[2]) - 273.15
        Temp = self.apply_noise(Temp)
        Temp = self.quantize(Temp)

        self.measurement = Temp
        self._save_data((time, Temp))

    def export_measured_data(self, filename, file_format="csv"):
        """Export the measured values to a file

        Parameters
        ----------
        filename : str
            Name of the file to export the values to
        file_format : str
            file_format of the file to export the values to. Options are "csv" and
            "json". Default is "csv".

        Returns
        -------
        None
        """
        self._generic_export_measured_data(
            filename=filename,
            file_format=file_format,
            data_labels=("t", "temperature"),
        )