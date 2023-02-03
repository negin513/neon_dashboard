"""
"""
import numpy as np
import xarray as xr
import dask.array as da
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from datetime import datetime
import pandas as pd


class MeshType:
    """
    An object for describing mesh or grid files.
    """

    def __init__(self, center_lats, center_lons, mask=None):
        self.mesh_name = None
        self.center_lats = center_lats
        self.center_lons = center_lons

        # -- dims of lat and lon (1d or 2d)
        self.lat_dims = len(self.center_lats.dims)
        self.lon_dims = len(self.center_lons.dims)
        self.check_lat_lon_dims()

        if mask is None:
            self.create_artificial_mask()
        else:
            self.mask = mask

    def __str__(self):
        """
        Converts ingredients of this class to string for printing.
        """
        return "{}\n{}".format(
            str(self.__class__),
            "\n".join(
                (
                    "{} = {}".format(str(key), str(self.__dict__[key]))
                    for key in sorted(self.__dict__)
                )
            ),
        )

    def check_lat_lon_dims(self):
        """
        Check lat and long dimensions to make sure they are either 1 or 2.
        """

        valid_dims = [1, 2]
        if self.lat_dims not in valid_dims:
            print(
                "Unrecognized grid! The dimension of latitude should be either 1 or 2 but it is {}.".format(
                    self.lat_dims
                )
            )

        if self.lon_dims not in valid_dims:
            print(
                "Unrecognized grid! The dimension of longitude should be either 1 or 2 but it is {}.".format(
                    self.lon_dims
                )
            )

    def get_lat_lon_points(self):
        """
        Get number of latitude and longitude points based on lats and lons provided.
        Basically calculates XxY
        """
        if self.lat_dims == 1:
            # -- if 1D lats and lons
            self.lats_size = self.center_lats.size
            self.lons_size = self.center_lons.size
        elif self.lat_dims == 2:
            # -- 2D lats and lons
            dims = self.center_lons.shape

            # -- convert 2D lats and lons to number x and y
            self.lons_size = dims[0]
            self.lats_size = dims[1]

    def create_artificial_mask(self):
        print("Creating Artificial Mask for This Region...")

        if self.lat_dims == 1:
            # -- 1D mask (lat x lon)
            lats_size = self.center_lats.size
            lons_size = self.center_lons.size
            print(lats_size)
            print(lons_size)
            mask = np.ones([lons_size, lats_size], dtype=np.int8)
        elif self.lat_dims == 2:
            # -- 2D mask
            mask = np.ones(
                tuple(self.center_lats.sizes.values()), dtype=np.int8
            )  # np.ones(center_lats.shape),dtype=np.int8)

        mask_da = da.from_array(mask)
        self.mask = mask_da

    def calculate_corners(self):
        """
        calculate corner coordinates by averaging neighbor cells
        """

        if self.lat_dims == 1:
            # -- 1D lats and lons
            # -- size of lats and lons
            lats_size = self.center_lats.size
            lons_size = self.center_lons.size

            # convert center points from 1d to 2d
            self.center_lat2d = da.broadcast_to(
                self.center_lats.values[None, :], (lons_size, lats_size)
            )
            self.center_lon2d = da.broadcast_to(
                self.center_lons.values[:, None], (lons_size, lats_size)
            )

        elif self.lat_dims == 2:
            # -- 2D lats and lons
            dims = self.center_lons.shape

            # -- convert 2D lats and lons to number x and y
            lons_size = dims[0]
            lats_size = dims[1]

            # -- convert to dask array
            self.center_lat2d = da.from_array(self.center_lats)
            self.center_lon2d = da.from_array(self.center_lons)

        # -----------------------------------------
        # -- calculate corner coordinates for latitude, counterclockwise order, imposing Fortran ordering
        center_lat2d_ext = da.from_array(
            np.pad(
                self.center_lat2d.compute(), (1, 1), mode="reflect", reflect_type="odd"
            )
        )

        # -- calculate corner lats
        upper_right = (
            center_lat2d_ext[1:-1, 1:-1]
            + center_lat2d_ext[0:-2, 1:-1]
            + center_lat2d_ext[1:-1, 2:]
            + center_lat2d_ext[0:-2, 2:]
        ) / 4.0
        upper_left = (
            center_lat2d_ext[1:-1, 1:-1]
            + center_lat2d_ext[0:-2, 1:-1]
            + center_lat2d_ext[1:-1, 0:-2]
            + center_lat2d_ext[0:-2, 0:-2]
        ) / 4.0
        lower_left = (
            center_lat2d_ext[1:-1, 1:-1]
            + center_lat2d_ext[1:-1, 0:-2]
            + center_lat2d_ext[2:, 1:-1]
            + center_lat2d_ext[2:, 0:-2]
        ) / 4.0
        lower_right = (
            center_lat2d_ext[1:-1, 1:-1]
            + center_lat2d_ext[1:-1, 2:]
            + center_lat2d_ext[2:, 1:-1]
            + center_lat2d_ext[2:, 2:]
        ) / 4.0

        self.corner_lat = da.stack(
            [
                upper_left.T.reshape((-1,)).T,
                lower_left.T.reshape((-1,)).T,
                lower_right.T.reshape((-1,)).T,
                upper_right.T.reshape((-1,)).T,
            ],
            axis=1,
        )

        # ------------------------------------------
        # calculate corner coordinates for longitude, counterclockwise order, imposing Fortran ordering
        center_lon2d_ext = da.from_array(
            np.pad(
                self.center_lon2d.compute(), (1, 1), mode="reflect", reflect_type="odd"
            )
        )

        # -- calculate corner lons
        upper_right = (
            center_lon2d_ext[1:-1, 1:-1]
            + center_lon2d_ext[0:-2, 1:-1]
            + center_lon2d_ext[1:-1, 2:]
            + center_lon2d_ext[0:-2, 2:]
        ) / 4.0
        upper_left = (
            center_lon2d_ext[1:-1, 1:-1]
            + center_lon2d_ext[0:-2, 1:-1]
            + center_lon2d_ext[1:-1, 0:-2]
            + center_lon2d_ext[0:-2, 0:-2]
        ) / 4.0
        lower_left = (
            center_lon2d_ext[1:-1, 1:-1]
            + center_lon2d_ext[1:-1, 0:-2]
            + center_lon2d_ext[2:, 1:-1]
            + center_lon2d_ext[2:, 0:-2]
        ) / 4.0
        lower_right = (
            center_lon2d_ext[1:-1, 1:-1]
            + center_lon2d_ext[1:-1, 2:]
            + center_lon2d_ext[2:, 1:-1]
            + center_lon2d_ext[2:, 2:]
        ) / 4.0

        self.corner_lon = da.stack(
            [
                upper_left.T.reshape((-1,)).T,
                lower_left.T.reshape((-1,)).T,
                lower_right.T.reshape((-1,)).T,
                upper_right.T.reshape((-1,)).T,
            ],
            axis=1,
        )

    def write_to_esmf_mesh(self, filename, area=None):
        """
        Writes ESMF Mesh to file
        """
        # create array with unique coordinate pairs
        # remove coordinates that are shared between the elements
        corner_pair = da.stack(
            [self.corner_lon.T.reshape((-1,)).T, self.corner_lat.T.reshape((-1,)).T],
            axis=1,
        )
        print(corner_pair)
        # REPLACED: node_coords = dd.from_dask_array(corner_pair).drop_duplicates().to_dask_array(lengths=True)
        # following reduces memory by %17
        node_coords = dd.from_dask_array(corner_pair).drop_duplicates().values
        print(node_coords.compute_chunk_sizes())

        # check size of unique coordinate pairs
        dims = mask.shape
        nlon = dims[0]
        nlat = dims[1]

        elem_conn_size = nlon * nlat + nlon + nlat + 1
        if node_coords.shape[0] != elem_conn_size:
            print(
                "The size of unique coordinate pairs is {} but expected size is {}!".format(
                    node_coords.shape[0], elem_conn_size
                )
            )
            print(
                "Please check the input file or try to force double precision with --double option. Exiting ..."
            )
            sys.exit(2)

        # create element connections
        corners = dd.concat(
            [
                dd.from_dask_array(c)
                for c in [
                    self.corner_lon.T.reshape((-1,)).T,
                    self.corner_lat.T.reshape((-1,)).T,
                ]
            ],
            axis=1,
        )
        corners.columns = ["lon", "lat"]
        elem_conn = corners.compute().groupby(["lon", "lat"], sort=False).ngroup() + 1
        elem_conn = da.from_array(elem_conn.to_numpy())

        # create new dataset for output
        out = xr.Dataset()

        out["origGridDims"] = xr.DataArray(
            np.array(self.center_lon2d.shape, dtype=np.int32), dims=("origGridRank")
        )
        print(out["origGridDims"])
        out["nodeCoords"] = xr.DataArray(
            node_coords, dims=("nodeCount", "coordDim"), attrs={"units": "degrees"}
        )

        out["elementConn"] = xr.DataArray(
            elem_conn.T.reshape((4, -1)).T,
            dims=("elementCount", "maxNodePElement"),
            attrs={"long_name": "Node indices that define the element connectivity"},
        )
        out.elementConn.encoding = {"dtype": np.int32}

        out["numElementConn"] = xr.DataArray(
            4 * np.ones(self.center_lon2d.size, dtype=np.int32),
            dims=("elementCount"),
            attrs={"long_name": "Number of nodes per element"},
        )

        out["centerCoords"] = xr.DataArray(
            da.stack(
                [
                    self.center_lon2d.T.reshape((-1,)).T,
                    self.center_lat2d.T.reshape((-1,)).T,
                ],
                axis=1,
            ),
            dims=("elementCount", "coordDim"),
            attrs={"units": "degrees"},
        )

        # -- add area if it is available
        if area:
            out["elementArea"] = xr.DataArray(
                area.T.reshape((-1,)).T,
                dims=("elementCount"),
                attrs={"units": "radians^2", "long_name": "area weights"},
            )

        # add mask
        out["elementMask"] = xr.DataArray(
            mask.T.reshape((-1,)).T, dims=("elementCount"), attrs={"units": "unitless"}
        )
        out.elementMask.encoding = {"dtype": np.int32}

        # -- force no '_FillValue' if not specified
        for var in out.variables:
            if "_FillValue" not in out[var].encoding:
                out[var].encoding["_FillValue"] = None

        # add global attributes
        out.attrs = {
            "title": "ESMF unstructured grid file for rectangular grid with {} dimension".format(
                "x".join(list(map(str, self.center_lats.shape)))
            ),
            #'created_by': os.path.basename(__file__),
            "date_created": "{}".format(datetime.now()),
            "conventions": "ESMFMESH",
        }

        # write output file
        if filename is not None:
            print("Writing ESMF Mesh to{} ...".format(filename))
            out.to_netcdf(filename)
