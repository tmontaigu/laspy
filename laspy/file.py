from __future__ import absolute_import
from laspy import base
from laspy import util
from laspy.header import HeaderManager
import os


class File(object):
    """ Base file object in laspy. Provides access to most laspy functionality,
    and holds references to the HeaderManager, Reader, and potentially Writer objects.
    """

    def __init__(
            self,
            filename,
            mode='r',
            header=None,
            vlrs=None,
            evlrs=None
    ):
        """Instantiate a file object to represent an LAS file.

        :arg filename: The filename to open
        :keyword header: A header open the file with. Not required in modes "r" and "rw"
        :type header: a :obj:`laspy.header.Header` instance
        :keyword mode: "r" for read, "rw" for modify/update, "w" for write, and "w+" for append (not implemented)
        :type mode: string
        :keyword in_srs: Input SRS to override the existing file's SRS with (not implemented)
        :type in_srs: a :obj:`laspy.SRS` instance
        :keyword out_srs: Output SRS to reproject points on-the-fly to as \
        they are read/written. (not implemented)
        :type out_srs: a :obj:`laspy.SRS` instance (not implemented)

        .. note::
            To open a file in write mode, you must provide a
            laspy.header.Header instance which will be immediately written to
            the file. If you provide a header instance in read mode, the
            values of that header will be used in place of those in the actual
            file.

        .. note::
            If a file is open for write, it cannot be opened for read and vice
            versa.

        >>> import laspy
        >>> f = laspy.file.File('file.las', mode='r')
        >>> for p in f:
        ...     print 'X,Y,Z: ', p.x, p.y, p.z

        >>> h = f.header
        >>> f2 = file.File('file2.las', mode = "w", header=h)
        >>> points = f.points
        >>> f2.points = points
        >>> f2.close()
        """
        if mode not in base.FILE_MODES:
            raise util.LaspyException("Mode {} not supported".format(self._mode))

        self.filename = os.path.abspath(filename)
        self._mode = mode.lower()
        self.file_manager = None

        if mode == 'w':
            raise NotImplementedError("lol")
        else:
            self.file_manager = base.Writer(self.filename, mode=self._mode)

        self._header = self.file_manager.get_header()
        self.add_extra_dimensions(self.file_manager.extra_dimensions)

    def add_extra_dimensions(self, extra_dims):
        if extra_dims:
            for dimension in extra_dims:
                dimname = dimension.name.decode().replace("\x00", "").replace(" ", "_").lower()
                self.add_property(dimname)

    def close(self, ignore_header_changes=False, minmax_mode="scaled"):
        """Closes the LAS file
        """
        self.file_manager.close()
        self.file_manager = None
        self._header = None

    def add_property(self, name):
        def fget(self):
            return self.file_manager.get_dimension(name)

        def fset(self, value):
            self.assert_write_mode()
            self.file_manager.set_dimension(name, value)

        setattr(self.__class__, name, property(fget, fset, None, None))

    def define_new_dimension(self, name, data_type, description):
        self.assert_write_mode()
        self.file_manager.define_new_dimension(name, data_type, description)
        self.add_property(name)

    def assert_write_mode(self):
        if self._mode == "r":
            raise util.LaspyException("File is not opened in a write mode.")

    def get_dimension(self, name):
        return self.file_manager.get_dimension(name)

    def set_dimension(self, name, value):
        self.assert_write_mode()
        self.file_manager.set_dimension(name, value)

    @property
    def header(self):
        """The file's :obj:`laspy.header.Header`

        .. note::
            The header class supports .xml and .etree methods.

        .. note::
            If the file is in append mode, the header will be overwritten in the
            file. Setting the header for the file when it is in read mode has no
            effect. If you wish to override existing header information with your
            own at read time, you must instantiate a new :obj:`laspy.file.File`
            instance.

        """
        return self.file_manager.get_header()

    @header.setter
    def header(self, header):
        """Sets the laspy.header.Header for the file.  If the file is in
        append mode, the header will be overwritten in the file."""
        if self._mode != "w+":
            raise util.LaspyException(
                "The header can only be set after file creation for files in append mode")
        self.file_manager.set_header(header)

    @property
    def points(self):
        """The point data from the file. Get or set the points as either a valid numpy array, or
        a list/array of laspy.base.Point instances. In write mode, the number of point records is set the
        first time a dimension or point array is supplied to the file."""
        return self.file_manager.get_points()

    @points.setter
    def points(self, new_points):
        """Set the points in the file from a valid numpy array, as generated from get_points,
        or a list/array of laspy.base.Point instances."""
        self.assert_write_mode()
        self.file_manager.set_points(new_points)

    def read(self, index, nice=True):
        """Reads the point at the given index"""
        if self.file_manager.get_pointrecordscount() >= index:
            return self.file_manager.get_point(index, nice)
        else:
            raise util.LaspyException("Index greater than point records count")

    @property
    def X(self):
        return self.file_manager.get_x()

    @X.setter
    def X(self, x):
        self.assert_write_mode()
        self.file_manager.set_x(x)

    @property
    def x(self):
        return self.file_manager.get_x(scale=True)

    @x.setter
    def x(self, x):
        self.assert_write_mode()
        self.file_manager.set_x(x, scale=True)

    @property
    def Y(self):
        return self.file_manager.get_y()

    @Y.setter
    def Y(self, y):
        self.assert_write_mode()
        self.file_manager.set_y(y)

    @property
    def y(self):
        return self.file_manager.get_y(scale=True)

    @y.setter
    def y(self, y):
        self.assert_write_mode()
        self.file_manager.set_y(y, scale=True)

    @property
    def Z(self):
        return self.file_manager.get_z()

    @Z.setter
    def Z(self, z):
        self.assert_write_mode()
        self.file_manager.set_z(z)

    @property
    def z(self):
        return self.file_manager.get_z(scale=True)

    @z.setter
    def z(self, z):
        self.assert_write_mode()
        self.file_manager.set_z(z, scale=True)

    @property
    def intensity(self):
        return self.file_manager.get_intensity()

    @intensity.setter
    def intensity(self, intensity):
        self.assert_write_mode()
        self.file_manager.set_intensity(intensity)

    @property
    def flag_byte(self):
        return self.file_manager.get_flag_byte()

    @flag_byte.setter
    def flag_byte(self, byte):
        self.assert_write_mode()
        self.file_manager.set_flag_byte(byte)

    @property
    def return_num(self):
        return self.file_manager.get_return_num()

    @return_num.setter
    def return_num(self, num):
        self.assert_write_mode()
        self.file_manager.set_return_num(num)

    @property
    def num_returns(self):
        return self.file_manager.get_num_returns()

    @num_returns.setter
    def num_returns(self, num):
        self.assert_write_mode()
        self.file_manager.set_num_returns(num)

    @property
    def scan_dir_flag(self):
        return self.file_manager.get_scan_dir_flag()

    @scan_dir_flag.setter
    def scan_dir_flag(self, flag):
        self.assert_write_mode()
        self.file_manager.set_scan_dir_flag(flag)

    @property
    def edge_flight_line(self):
        return self.file_manager.get_edge_flight_line()

    @edge_flight_line.setter
    def edge_flight_line(self, line):
        self.assert_write_mode()
        self.file_manager.set_edge_flight_line(line)

    @property
    def raw_classification(self):
        return self.file_manager.get_raw_classification()

    @raw_classification.setter
    def raw_classification(self, classification):
        self.assert_write_mode()
        self.file_manager.set_raw_classification(classification)

    @property
    def classification(self):
        return self.file_manager.get_classification()

    @classification.setter
    def classification(self, classification):
        self.assert_write_mode()
        self.file_manager.set_classification(classification)

    @property
    def classification_flags(self):
        return self.file_manager.get_classification_flags()

    @classification_flags.setter
    def classification_flags(self, value):
        self.assert_write_mode()
        self.file_manager.set_classification_flags(value)

    @property
    def scanner_channel(self):
        return self.file_manager.get_scanner_channel()

    @scanner_channel.setter
    def scanner_channel(self, value):
        self.assert_write_mode()
        self.file_manager.set_scanner_channel(value)

    @property
    def synthetic(self):
        return self.file_manager.get_synthetic()

    @synthetic.setter
    def synthetic(self, synthetic):
        self.assert_write_mode()
        self.file_manager.set_synthetic(synthetic)

    @property
    def key_point(self):
        return self.file_manager.get_key_point()

    @key_point.setter
    def key_point(self, pt):
        self.assert_write_mode()
        self.file_manager.set_key_point(pt)

    @property
    def withheld(self):
        return self.file_manager.get_withheld()

    @withheld.setter
    def withheld(self, withheld):
        self.assert_write_mode()
        self.file_manager.set_withheld(withheld)

    @property
    def overlap(self):
        return self.file_manager.get_overlap()

    @overlap.setter
    def overlap(self, overlap):
        self.assert_write_mode()
        self.file_manager.set_overlap(overlap)
        return

    def get_scan_angle_rank(self):
        return self.file_manager.get_scan_angle_rank()

    def set_scan_angle_rank(self, rank):
        self.assert_write_mode()
        self.file_manager.set_scan_angle_rank(rank)
        return

    scan_angle_rank = property(get_scan_angle_rank, set_scan_angle_rank, None, None)

    def get_scan_angle(self):
        return self.file_manager.get_scan_angle()

    def set_scan_angle(self, rank):
        self.assert_write_mode()
        self.file_manager.set_scan_angle(rank)
        return

    scan_angle = property(get_scan_angle, set_scan_angle, None, None)

    def get_user_data(self):
        return self.file_manager.get_user_data()

    def set_user_data(self, data):
        self.assert_write_mode()
        self.file_manager.set_user_data(data)
        return

    user_data = property(get_user_data, set_user_data, None, None)

    def get_pt_src_id(self):
        return self.file_manager.get_pt_src_id()

    def set_pt_src_id(self, data):
        self.assert_write_mode()
        self.file_manager.set_pt_src_id(data)
        return

    pt_src_id = property(get_pt_src_id, set_pt_src_id, None, None)

    def get_gps_time(self):
        return self.file_manager.get_gps_time()

    def set_gps_time(self, data):
        self.assert_write_mode()
        self.file_manager.set_gps_time(data)
        return

    gps_time = property(get_gps_time, set_gps_time, None, None)

    def get_red(self):
        return self.file_manager.get_red()

    def set_red(self, red):
        self.assert_write_mode()
        self.file_manager.set_red(red)

    red = property(get_red, set_red, None, None)
    Red = red

    def get_green(self):
        return self.file_manager.get_green()

    def set_green(self, green):
        self.assert_write_mode()
        self.file_manager.set_green(green)
        return

    green = property(get_green, set_green, None, None)
    Green = green

    def get_blue(self):
        return self.file_manager.get_blue()

    def set_blue(self, blue):
        self.assert_write_mode()
        self.file_manager.set_blue(blue)
        return

    blue = property(get_blue, set_blue)
    Blue = blue

    def get_wave_packet_desc_index(self):
        return self.file_manager.get_wave_packet_desc_index()

    def set_wave_packet_desc_index(self, idx):
        self.assert_write_mode()
        self.file_manager.set_wave_packet_desc_index(idx)
        return

    def get_nir(self):
        return self.file_manager.get_nir()

    def set_nir(self, value):
        self.assert_write_mode()
        self.file_manager.set_nir(value)
        return

    nir = property(get_nir, set_nir, None, None)

    wave_packet_desc_index = property(get_wave_packet_desc_index,
                                      set_wave_packet_desc_index, None, None)

    def get_byte_offset_to_waveform_data(self):
        return self.file_manager.get_byte_offset_to_waveform_data()

    def set_byte_offset_to_waveform_data(self, idx):
        self.assert_write_mode()
        self.file_manager.set_byte_offset_to_waveform_data(idx)
        return

    byte_offset_to_waveform_data = property(get_byte_offset_to_waveform_data,
                                            set_byte_offset_to_waveform_data,
                                            None, None)

    def get_waveform_packet_size(self):
        return self.file_manager.get_waveform_packet_size()

    def set_waveform_packet_size(self, size):
        self.assert_write_mode()
        self.file_manager.set_waveform_packet_size(size)
        return

    waveform_packet_size = property(get_waveform_packet_size,
                                    set_waveform_packet_size,
                                    None, None)

    def get_return_point_waveform_loc(self):
        return self.file_manager.get_return_point_waveform_loc()

    def set_return_point_waveform_loc(self, loc):
        self.assert_write_mode()
        self.file_manager.set_return_point_waveform_loc(loc)
        return

    return_point_waveform_loc = property(get_return_point_waveform_loc,
                                         set_return_point_waveform_loc,
                                         None, None)

    def get_x_t(self):
        return self.file_manager.get_x_t()

    def set_x_t(self, x):
        self.assert_write_mode()
        self.file_manager.set_x_t(x)
        return

    x_t = property(get_x_t, set_x_t, None, None)

    def get_y_t(self):
        return self.file_manager.get_y_t()

    def set_y_t(self, y):
        self.assert_write_mode()
        self.file_manager.set_y_t(y)
        return

    y_t = property(get_y_t, set_y_t, None, None)

    def get_z_t(self):
        return self.file_manager.get_z_t()

    def set_z_t(self, z):
        self.assert_write_mode()
        self.file_manager.set_z_t(z)
        return

    z_t = property(get_z_t, set_z_t, None, None)

    def get_extra_bytes(self):
        return self.file_manager.get_extra_bytes()

    def set_extra_bytes(self, new):
        self.assert_write_mode()
        self.file_manager.set_extra_bytes(new)

    doc = '''It is possible to specify a data_record_length longer than the default, 
            and the extra space is treated by laspy as raw bytes accessable via this extra_bytes property. 
            This dimension is only assignable for files in write mode which were instantiated with the appropriate
            data_record_length from the header.'''
    extra_bytes = property(get_extra_bytes, set_extra_bytes, None, doc)

    def __iter__(self):
        """Iterator support (read mode only)

          >>> points = []
          >>> for i in f:
          ...   points.append(i)
          ...   print i # doctest: +ELLIPSIS
          <laspy.base.Point object at ...>
        """
        if self._mode == "r":
            self.at_end = False
            p = self.file_manager.get_point(0)
            while p and not self.at_end:

                yield p
                p = self.file_manager.get_next_point()
                if not p:
                    self.at_end = True
            else:
                self.close()
        else:
            raise StopIteration("Iteration only supported in read mode, try using FileObject.points")

    def __getitem__(self, index):
        """Index and slicing support

          >>> out = f[0:3]
          [<laspy.base.Point object at ...>,
          <laspy.base.Point object at ...>,
          <laspy.base.Point object at ...>]
        """
        if isinstance(index, range):
            return [self.read(i) for i in index]
        else:
            return self.read(index)

    def __len__(self):
        """Returns the number of points in the file according to the header"""
        return self.header.point_records_count

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # Updating header changes is slow.
        self.close(ignore_header_changes=True)

    def get_point_format(self):
        return self.file_manager.point_format

    doc = '''The point format of the file, stored as a laspy.util.Format instance. Supports .xml and .etree methods.'''
    point_format = property(get_point_format, None, None, doc)
