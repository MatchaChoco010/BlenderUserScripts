bl_info = {
    "name": "save-load-shapes",
    "author": "ORITO Itsuki",
    "description": "",
    "blender": (3, 4, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

from . import auto_load  # noqa: E402

auto_load.init()


def register():
    auto_load.register()


def unregister():
    auto_load.unregister()
