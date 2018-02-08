#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, CMake


class LibpngConan(ConanFile):
    name = "libpng"
    version = "1.6.34"
    description = "libpng is the official PNG file format reference library. "
    url="http://github.com/bitprim/conan-libpng"
    license = "Libpng"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "FindPNG.cmake"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"

    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    build_policy = "missing"

    ZIP_FOLDER_NAME = "%s-%s" % (name, version)


    @property
    def msvc_mt_build(self):
        return "MT" in str(self.settings.compiler.runtime)

    @property
    def fPIC_enabled(self):
        if self.settings.compiler == "Visual Studio":
            return False
        else:
            return self.options.fPIC

    @property
    def is_shared(self):
        # if self.options.shared and self.msvc_mt_build:
        if self.settings.compiler == "Visual Studio" and self.msvc_mt_build:
            return False
        else:
            return self.options.shared

    def requirements(self):
        self.requires.add("zlib/1.2.11@bitprim/stable")

    def config_options(self):
        self.output.info('*-*-*-*-*-* def config_options(self):')
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")

            if self.options.shared and self.msvc_mt_build:
                self.options.remove("shared")

    def configure(self):
        del self.settings.compiler.libcxx       #Pure-C Library
        
    def source(self):
        base_url = "https://sourceforge.net/projects/libpng/files/libpng16/"
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
        try:
            tools.download("%s/%s/%s" % (base_url, self.version, zip_name), zip_name)
        except Exception:
            tools.download("%s/older-releases/%s/%s" % (base_url, self.version, zip_name), zip_name)
        tools.unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            tools.replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}',
                                  'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/$<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}')
        cmake = CMake(self)
        cmake.definitions["PNG_TESTS"] = "OFF"
        cmake.definitions["PNG_SHARED"] = self.is_shared
        cmake.definitions["PNG_STATIC"] = not self.is_shared
        cmake.definitions["PNG_DEBUG"] = "OFF" if self.settings.build_type == "Release" else "ON"

        # if self.settings.compiler != "Visual Studio":
        #     cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.fPIC_enabled
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.fPIC_enabled

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("FindPNG.cmake")

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "gcc":
                self.cpp_info.libs = ["png"]
            else:
                if self.is_shared:
                    self.cpp_info.libs = ['libpng16']
                else:
                    self.cpp_info.libs = ['libpng16_static']
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs[0] += "d"
        else:
            self.cpp_info.libs = ["png16d" if self.settings.build_type == "Debug" else "png16"]
            if self.settings.os == "Linux":
                self.cpp_info.libs.append("m")
