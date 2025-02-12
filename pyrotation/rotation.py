#!/usr/bin/python
# -*- coding: latin-1 -*-

"""Quaternion class and further rotation related functions
"""
import numpy as np
cos = np.cos
sin = np.sin


class Quaternion(object):
    ''' Quaternion class

    The quaternion convention used in this class is

    q = [w, x, y, z]

    encoding a rotation around axis "a" with angle "theta" by

    w = cos(theta/2)
    [x,y,z] = a*sin(theta/2)

    The convention and the mathematical equations are adapted from:

    "Quaternion kinematics for the error-state Kalman filter" by Joan Solà
    http://www.iri.upc.edu/people/jsola/JoanSola/objectes/notes/kinematics.pdf
    '''

    def __init__(self, q=None):
        """initialize quaternion to valid values (norm=1)
        Attributes:
        q (numpy.ndarray or list, optional): quaternion [w,x,y,z]
        """
        if q is None:
            self.set_default()
            return

        # allow list initalization
        if isinstance(q, list):
            q = np.array(q)

        # make 1D version of q
        q_flat = q.flatten()
        if len(q_flat) != 4:
            print('cannot set quaternion from array size {}. Using default values'.format(len(q_flat)))
            self.set_default()
            return

        self.q = q_flat
        self.normalize()

    @property
    def w(self):
        """access w element of the quaternion"""
        return self.q[0]

    @property
    def x(self):
        """access x element of the quaternion"""
        return self.q[1]

    @property
    def y(self):
        """access y element of the quaternion"""
        return self.q[2]

    @property
    def z(self):
        """access z element of the quaternion"""
        return self.q[3]

    def set_default(self,):
        """set values representing a neutral quaternion (zero rotation)"""
        self.q = np.array([1, 0, 0, 0], dtype=float)

    def normalize(self,):
        """scale quaternion such that its 2-norm is equal to one"""
        norm = np.linalg.norm(self.q)
        if norm > 0:
            self.q *= 1.0 / norm
        else:
            print('Quaternion cannot be normalized. Setting to default values')
            self.set_default()

    def __mul__(self, other):
        """overload multiplication operator"""
        return Quaternion(np.dot(self.get_left_mult_matrix(), other.q))

    def get_left_mult_matrix(self,):
        """get multiplication matrix that is equivalent to quaternion multiplication from the left

        Example: q1*q2 = M(q1)*q2 where M(q1) is the left multiplication matrix
        """
        return np.array([
            [self.w, -self.x, -self.y, -self.z],
            [self.x, self.w, -self.z, self.y],
            [self.y, self.z, self.w, -self.x],
            [self.z, -self.y, self.x, self.w]])

    def get_right_mult_matrix(self,):
        """get multiplication matrix that is equivalent to quaternion multiplication from the right

        Example: q1*q2 = M(q2)*q1 where M(q2) is the left multiplication matrix
        """
        return np.array([
            [self.w, -self.x, -self.y, -self.z],
            [self.x, self.w, self.z, -self.y],
            [self.y, -self.z, self.w, self.x],
            [self.z, self.y, -self.x, self.w]])

    def q_dot(self, omega, frame='body'):
        """calculate the quaternion derivative as a result to angular velocity"""
        if frame == 'body':
            return 0.5 * np.dot(self.get_left_mult_matrix()[:, 1:], omega)
        if frame == 'inertial':
            return 0.5 * np.dot(self.get_right_mult_matrix()[:, 1:], omega)
        print('frame "{}" invalid. Use "body" or "inertial"'.format(frame))
        return np.zeros(4)

    def inverse(self,):
        """calculate the inverse q_inv of the quaternion q such that q*q_inv = [1,0,0,0] (unit quaternion)

        Since q(axis, theta) = [cos(theta/2), axis*sin(theta/2)] and its inverse is q_inv = q(axis, -theta), the inverse of q is q_inv = [cos(-theta/2), axis*sin(-theta/2)] = [cos(theta/2), -axis*sin(theta/2)]. Hence, to get from q to q_inv, the [x,y,z] entries have to be inverted.
        """
        return Quaternion(np.array([self.w, -self.x, -self.y, -self.z]))

    def rotation_matrix(self,):
        """calculate rotation matrix equivalent of the quaternion"""
        qw_2 = self.w**2
        qx_2 = self.x**2
        qy_2 = self.y**2
        qz_2 = self.z**2
        qwqx = self.w * self.x
        qwqy = self.w * self.y
        qwqz = self.w * self.z
        qxqy = self.x * self.y
        qxqz = self.x * self.z
        qyqz = self.y * self.z

        rot = np.eye(3)
        rot[0, 0] = qw_2 + qx_2 - qy_2 - qz_2
        rot[1, 1] = qw_2 - qx_2 + qy_2 - qz_2
        rot[2, 2] = qw_2 - qx_2 - qy_2 + qz_2

        rot[0, 1] = 2 * (qxqy - qwqz)
        rot[1, 0] = 2 * (qxqy + qwqz)

        rot[0, 2] = 2 * (qxqz + qwqy)
        rot[2, 0] = 2 * (qxqz - qwqy)

        rot[1, 2] = 2 * (qyqz - qwqx)
        rot[2, 1] = 2 * (qyqz + qwqx)

        return rot

    def get_roll_pitch_yaw(self,):
        """calculate roll, pitch and yaw angle equivalent of the quaternion

        This rotation sequence is defined as a rotation of the body frame about the body frame's z-axis by angle yaw, followed by a rotation about the body frame's y-axis by angle pitch, followed by a rotation about the body frame's x-axis by angle roll.

        The angles can be calculated from the quaternion by using the function rot_to_roll_pitch_yaw and replacing the rotation matrix entries with the quaternion expressions derived in the member function rotation_matrix: q.get_roll_pitch_yaw() = rot_to_roll_pitch_yaw(q.rotation_matrix())
        """
        sin_p = 2 * (self.w * self.y - self.z * self.x)
        if sin_p >= 1:
            pitch = np.pi / 2
            yaw = 0
            roll = np.arctan2(self.x * self.y - self.w * self.z, self.x * self.z + self.w * self.y)
        elif sin_p <= -1:
            pitch = -np.pi / 2
            yaw = 0
            roll = np.arctan2(-self.x * self.y + self.w * self.z, -
                              self.x * self.z - self.w * self.y)
        else:
            pitch = np.arcsin(sin_p)
            roll = np.arctan2(2 * (self.w * self.x + self.y * self.z),
                              1 - 2 * (self.x**2 + self.y**2))
            yaw = np.arctan2(2 * (self.w * self.z + self.x * self.y),
                             1 - 2 * (self.y**2 + self.z**2))

        return np.array([roll, pitch, yaw])

# further functions for creating quaternions


def quat_from_angle_axis(angle, axis, norm=None):
    """calculate quaternion from angle and rotation axis"""
    if angle == 0:
        return Quaternion()
    if norm is None:
        norm = np.linalg.norm(axis)
    if norm > 0:
        return Quaternion(np.concatenate(
            [[cos(0.5 * angle)], axis * sin(0.5 * angle) / norm]))
    print('rotation axis has norm zero, rotation undefined')
    return Quaternion()


def quat_from_angle_vector(angle_vec):
    """calculate quaternion from an angle vector

    An angle vector is a 3x1 vector parametrizing a rotation. It points in the direction of the rotation axis, and its length is the rotation angle.
    """
    angle = np.linalg.norm(angle_vec)
    return quat_from_angle_axis(angle, angle_vec, norm=angle)


def quat_from_roll_pitch_yaw(roll, pitch, yaw):
    """calculate quaternion from roll, pitch and yaw angle

    This rotation sequence is defined as a rotation about the body frame's z-axis by angle yaw, followed by a rotation about the (new) body frame's y-axis by angle pitch, followed by a rotation about the body frame's x-axis by angle roll.
    """
    cos_p = cos(pitch * 0.5)
    sin_p = sin(pitch * 0.5)
    cos_r = cos(roll * 0.5)
    sin_r = sin(roll * 0.5)
    cos_y = cos(yaw * 0.5)
    sin_y = sin(yaw * 0.5)

    qw = cos_p * cos_r * cos_y + sin_p * sin_r * sin_y
    qx = cos_p * sin_r * cos_y - sin_p * cos_r * sin_y
    qy = sin_p * cos_r * cos_y + cos_p * sin_r * sin_y
    qz = cos_p * cos_r * sin_y - sin_p * sin_r * cos_y

    return Quaternion([qw, qx, qy, qz])

# functions for creating rotation matrices


def rot_from_angle_axis(angle, axis, norm=None):
    """calculate rotation matrix from angle and rotation axis"""
    if angle == 0:
        return np.eye(3)
    if norm is None:
        norm = np.linalg.norm(axis)
    if norm > 0:
        axis = axis / norm
        skew = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
        return np.eye(3) + sin(angle) * skew + (1 - cos(angle)) * np.dot(skew, skew)
    print('rotation axis has norm zero, rotation undefined')
    return np.eye(3)


def rot_from_angle_vector(angle_vec):
    """calculate rotation matrix from an angle vector"""
    angle = np.linalg.norm(angle_vec)
    return rot_from_angle_axis(angle, angle_vec, norm=angle)


def rot_from_roll_pitch_yaw(roll, pitch, yaw):
    """calculate rotation matrix from roll, pitch and yaw

    This result can be generated symbolically by rot_z(yaw) * rot_y(pitch) * rot_x(roll).
    """
    return np.array([[cos(pitch) * cos(yaw),
                      sin(pitch) * sin(roll) * cos(yaw) - sin(yaw) * cos(roll),
                      sin(pitch) * cos(roll) * cos(yaw) + sin(roll) * sin(yaw)],
                     [sin(yaw) * cos(pitch),
                      sin(pitch) * sin(roll) * sin(yaw) + cos(roll) * cos(yaw),
                      sin(pitch) * sin(yaw) * cos(roll) - sin(roll) * cos(yaw)],
                     [-sin(pitch),
                      sin(roll) * cos(pitch),
                      cos(pitch) * cos(roll)]])


def rot_x(angle):
    """calculate rotation matrix for a rotation around the x-axis"""
    c = cos(angle)
    s = sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(angle):
    """calculate rotation matrix for a rotation around the y-axis"""
    c = cos(angle)
    s = sin(angle)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(angle):
    """calculate rotation matrix for a rotation around the z-axis"""
    c = cos(angle)
    s = sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def rot_to_roll_pitch_yaw(rot):
    """calculate roll, pitch and yaw angle equivalent of the rotation matrix

    This rotation sequence is defined as a rotation of the body frame about the body frame's z-axis by angle yaw, followed by a rotation about the body frame's y-axis by angle pitch, followed by a rotation about the body frame's x-axis by angle roll.

    By inspecting the elements in the rotation matrix in the function rot_from_roll_pitch_yaw, and by using the trigonometric relation tan(x) = sin(x) / cos(x), the rotation angles can be calculated from the entries of the rotation matrix.

    In case of singularity (pitch = +-pi/2), the rotation of the x and z-axis are aligned. The sum of roll+yaw is given in this case, but it is undefined how large the individual terms are. Here, yaw = 0 is returned, and the roll angle accounts for the full x/z rotation.
    """
    # rot[2, 0] = -sin(pitch)
    sin_p = -rot[2, 0]
    if sin_p >= 1:
        pitch = np.pi / 2
        yaw = 0
        # for pitch = pi/2: rot[0,1] = sin(roll - yaw); rot[0,2] = cos(roll - yaw)
        roll = np.arctan2(rot[0, 1], rot[0, 2])
    elif sin_p <= -1:
        pitch = -np.pi / 2
        yaw = 0
        # for pitch = -pi/2: rot[0,1] = -sin(roll + yaw); rot[0,2] = -cos(roll + yaw)
        roll = np.arctan2(-rot[0, 1], -rot[0, 2])
    else:
        pitch = np.arcsin(sin_p)
        # rot[2,1] = sin(roll)*cos(pitch); rot[2,2] = cos(roll)*cos(pitch)
        roll = np.arctan2(rot[2, 1], rot[2, 2])
        # rot[1,0] = sin(yaw)*cos(pitch); rot[0,0] = cos(yaw)*cos(pitch)
        yaw = np.arctan2(rot[1, 0], rot[0, 0])

    return np.array([roll, pitch, yaw])
