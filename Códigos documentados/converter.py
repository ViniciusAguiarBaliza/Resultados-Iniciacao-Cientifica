import json

import numpy as np
from model.body import Body
from model.keplerian_body import KeplerianBody
from scipy import optimize

from model.solar_probe import SolarProbe
from utils.decorators import log_time

#JSON_PATH = '../resources/solar-system.json'

# Sets 'JSON_PATH' as​a file with solar system data
JSON_PATH = "C:\\Users\\vinic\\Documents\\UFMG\\4° Semestre\\" \
            "IC\\myLocal_n-body-simulator\\myLocal_n-body-simulator\\" \
            "resources\\solar-system.json"


# Sets "rotation_z" as an array that depends on an 'alpha' angle
def rotation_z(alpha):
    return np.array([[np.cos(alpha), np.sin(alpha), 0],
                     [-np.sin(alpha), np.cos(alpha), 0],
                     [0, 0, 1]])


# Sets "rotation_x" as an array that depends on an 'alpha' angle
def rotation_x(alpha):
    return np.array([[1, 0, 0],
                     [0, np.cos(alpha), np.sin(alpha)],
                     [0, -np.sin(alpha), np.cos(alpha)]])


def get_rotation_matrix(keplerian_body):

    # Converts argument of periapsis ('omega') from degrees to radians
    omega_rad = np.deg2rad(keplerian_body.omega)

    # Converts inclination ('i') from degrees to radians
    i_rad = np.deg2rad(keplerian_body.i)

    # Converts longitude of ascending node ('OMEGA')
    # from degrees to radians
    OMEGA_RAD = np.deg2rad(keplerian_body.OMEGA)

    # Makes the product between the "rotation_z" array
    # (being 'alpha' = -'OMEGA_RAD ') and the
    # "rotation_x" array (being 'alpha' = -'i_rad')
    r1 = np.dot(rotation_z(-OMEGA_RAD), rotation_x(-i_rad))

    # Makes the product between the result of the 'r1' array and
    # the "rotation_z" array (being 'alpha' = -'omega_rad ')
    r2 = np.dot(r1, rotation_z(-omega_rad))
    return r2


# Records date and time of operations
@log_time
# Function that transforms Kleperian elements
# into Cartesian elements for a body ('Body')
def kepler_to_cartesian(keplerian_body):
    """
    :param keplerian_body: 'KeplerianBody'
    :return: 'Body'
    """
    if keplerian_body.central_body is None:
        keplerian_body.central_body = kepler_to_cartesian(
                                      keplerian_body.keplerian_central_body)

    # Loads a file with solar system data
    with open(JSON_PATH) as json_file:
        data = json.load(json_file)
        # Use the file to get data from a specific
        # Kleperian body and a central body
        astra = data[keplerian_body.central_body.name.lower()]

    # Sets the standard gravitational parameter ('mu')
    # of the body according to the file
    mu = astra['mu']

    # Sets the mean motion ('n')
    n = np.sqrt(mu / keplerian_body.a ** 3)

    # Tests elements of the mean anomaly ('M') by NaN
    # and returns a Boolean array
    if np.isnan(keplerian_body.M):
    # If it returns "True":

        # Converts true anomaly ('theta') from degrees to radians
        theta = np.deg2rad(keplerian_body.theta)

        # Sets the eccentric anomaly ('U')
        U = np.arctan2(np.sqrt(1 - keplerian_body.e ** 2) * np.sin(theta),
                        keplerian_body.e + np.cos(theta))

    # If it doesn't return "True":
    else:
        # Converts mean anomaly ('M') from degrees to radians
        M = np.deg2rad(keplerian_body.M)

        # Sets the eccentric anomaly function ('U_function')
        # and its derived ('U_prime')
        U_function = lambda u: u - keplerian_body.e * np.sin(u) - M
        U_prime = lambda u: 1 - keplerian_body.e * np.cos(u)

        # Applies Newton-Raphson method to find eccentric anomaly ('U')
        U = optimize.newton(func = U_function, x0=M,
                            fprime = U_prime, tol = 1e-8)

        # Sets the true anomaly ('theta')
        theta = 2 * np.arctan2(np.sqrt(1 - keplerian_body.e) * np.sin(U / 2),
                               np.sqrt(1 - keplerian_body.e) * np.cos(U / 2))

    # Gets central body distance ('rc')
    rc = keplerian_body.a * (1 - keplerian_body.e * np.cos(U))

    # Sets position and velocity on local coordinates system
    # ('position' and 'velocity')
    position = [keplerian_body.a * (np.cos(U) - keplerian_body.e),
                (keplerian_body.a * np.sin(U) *
                 np.sqrt(1 - keplerian_body.e ** 2)),
                0]

    velocity = np.array([-n * keplerian_body.a ** 2 / rc * np.sin(U),
                         (n * keplerian_body.a ** 2 / rc * np.cos(U) *
                          np.sqrt(1 - keplerian_body.e ** 2)),
                         0])

    # Rotates the coordinate system to the inertial frame
    # using function 3 ("get_rotation_matrix") previously created
    rotation_matrix = get_rotation_matrix(keplerian_body)

    # Sets the position and velocity in relation to the central body of
    # the 2-body system ('relative_position' and 'relative_velocity')
    relative_position = np.dot(rotation_matrix, position)

    relative_velocity = np.dot(rotation_matrix, velocity)

    # Sets the position and velocity in relation to the inertial axis
    # of the whole system ('absolute_position' and 'absolute_velocity')
    absolute_position = (relative_position +
                         keplerian_body.central_body.position)

    absolute_velocity = (relative_velocity +
                         keplerian_body.central_body.velocity)

    # Returns the 'Body' object with its data
    return Body(keplerian_body.name, keplerian_body.mass, absolute_position,
                absolute_velocity, keplerian_body.radius)


# Function that transforms Kleperian elements
# into Cartesian elements for a solar probe ('SolarProbe')
def probe_kepler_to_cartesian(keplerian_solar_probe):
    """
    :param keplerian_solar_probe: KeplerianSolarProbe
    :return: SolarProbe
    """
    # Applies the function 4 ("kepler_to_cartesian")
    # previously created for a solar probe
    body = kepler_to_cartesian(keplerian_solar_probe)

    #Returns the 'SolarProbe' object with its data
    return SolarProbe(
        body.name, body.mass, body.position, body.velocity, body.radius,
        keplerian_solar_probe.alpha,
        keplerian_solar_probe.delta,
        keplerian_solar_probe.area,
        keplerian_solar_probe.r_diff,
        keplerian_solar_probe.r_spec,
        keplerian_solar_probe.e_f,
        keplerian_solar_probe.e_b,
        keplerian_solar_probe.a_f,
        keplerian_solar_probe.a_b,
        keplerian_solar_probe.chi_f,
        keplerian_solar_probe.chi_b, )


if __name__ == '__main__':

    # Sets the "Earth" as the central body
    # (with its mass, position, velocity and radius)
    central_body = Body("earth", 5.97237e24, [0, 0, 0], [0, 0, 0], 6378.1366)

    # Sets the "Hubble" as an example of an keplerian body
    # (with its mass, semi-major axis, eccentricity,
    # inclination, argument of periapsis,
    # longitude of ascending node, radius and true anomaly)
    example = KeplerianBody("HUBBLE", 10, 6.922453751349309e3, 1.1591437e-3,
                            2.858871232061450E+01, 4.804080043054086E+01,
                            8.037273861036857E+01, 42, central_body,
                            theta=3.321400340149752E+02)
    print(example, kepler_to_cartesian(example),
          sep='\n===================\n')
