# -*- coding: utf-8 -*-
import os
import fnmatch
from functools import total_ordering
from conans.errors import ConanInvalidConfiguration, ConanException
from conans import ConanFile, AutoToolsBuildEnvironment, tools


@total_ordering
class OpenSSLVersion(object):
    def __init__(self, version_str):
        self._pre = ""

        tokens = version_str.split("-")
        if len(tokens) > 1:
            self._pre = tokens[1]
        version_str = tokens[0]

        tokens = version_str.split(".")
        self._major = int(tokens[0])
        self._minor = 0
        self._patch = 0
        self._build = ""
        if len(tokens) > 1:
            self._minor = int(tokens[1])
            if len(tokens) > 2:
                self._patch = tokens[2]
                if self._patch[-1].isalpha():
                    self._build = self._patch[-1]
                    self._patch = self._patch[:1]
                self._patch = int(self._patch)

    @property
    def base(self):
        return "%s.%s.%s" % (self._major, self._minor, self._patch)

    @property
    def as_list(self):
        return [self._major, self._minor, self._patch, self._build, self._pre]

    def __eq__(self, other):
        return self.compare(other) == 0

    def __lt__(self, other):
        return self.compare(other) == -1

    def __hash__(self):
        return hash(self.as_list)

    def compare(self, other):
        if not isinstance(other, OpenSSLVersion):
            other = OpenSSLVersion(other)
        if self.as_list == other.as_list:
            return 0
        elif self.as_list < other.as_list:
            return -1
        else:
            return 1


class OpenSSLConan(ConanFile):
    name = "OpenSSL"
    settings = "os", "compiler", "arch", "build_type"
    url = "http://github.com/conan-community/conan-openssl"
    homepage = "https://github.com/openssl/openssl"
    author = "Conan Community"
    license = "OpenSSL"
    topics = ("conan", "openssl", "ssl", "tls", "encryption", "security")
    description = "A toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols"
    options = {"no_threads": [True, False],
               "no_zlib": [True, False],
               "shared": [True, False],
               "fPIC": [True, False],
               "no_asm": [True, False],
               "386": [True, False],
               "no_sse2": [True, False],
               "no_bf": [True, False],
               "no_cast": [True, False],
               "no_des": [True, False],
               "no_dh": [True, False],
               "no_dsa": [True, False],
               "no_hmac": [True, False],
               "no_md2": [True, False],
               "no_md5": [True, False],
               "no_mdc2": [True, False],
               "no_rc2": [True, False],
               "no_rc4": [True, False],
               "no_rc5": [True, False],
               "no_rsa": [True, False],
               "no_sha": [True, False],
               "no_async": [True, False],
               "no_dso": [True, False],
               "capieng_dialog": [True, False],
               "openssldir": "ANY"}
    default_options = {key: False for key in options.keys()}
    default_options["fPIC"] = True
    default_options["openssldir"] = None
    _source_subfolder = "sources"

    def build_requirements(self):
        # useful for example for conditional build_requires
        if tools.os_info.is_windows:
            self.build_requires("strawberryperl/5.30.0.1@conan/stable")
            if not self.options.no_asm and not tools.which("nasm"):
                self.build_requires("nasm/2.13.01@conan/stable")

    @property
    def _full_version(self):
        return OpenSSLVersion(self.version)

    def source(self):
        sha256 = {
            "1.0.2": "8c48baf3babe0d505d16cfc0cf272589c66d3624264098213db0fb00034728e9",
            "1.0.2a": "15b6393c20030aab02c8e2fe0243cb1d1d18062f6c095d67bca91871dc7f324a",
            "1.0.2b": "d5d488cc9f0a07974195a7427094ea3cab9800a4e90178b989aa621fbc238e3f",
            "1.0.2c": "0038ba37f35a6367c58f17a7a7f687953ef8ce4f9684bbdec63e62515ed36a83",
            "1.0.2d": "671c36487785628a703374c652ad2cebea45fa920ae5681515df25d9f2c9a8c8",
            "1.0.2e": "e23ccafdb75cfcde782da0151731aa2185195ac745eea3846133f2e05c0e0bff",
            "1.0.2f": "932b4ee4def2b434f85435d9e3e19ca8ba99ce9a065a61524b429a9d5e9b2e9c",
            "1.0.2g": "b784b1b3907ce39abf4098702dade6365522a253ad1552e267a9a0e89594aa33",
            "1.0.2h": "1d4007e53aad94a5b2002fe045ee7bb0b3d98f1a47f8b2bc851dcd1c74332919",
            "1.0.2i": "9287487d11c9545b6efb287cdb70535d4e9b284dd10d51441d9b9963d000de6f",
            "1.0.2j": "e7aff292be21c259c6af26469c7a9b3ba26e9abaaffd325e3dccc9785256c431",
            "1.0.2k": "6b3977c61f2aedf0f96367dcfb5c6e578cf37e7b8d913b4ecb6643c3cb88d8c0",
            "1.0.2l": "ce07195b659e75f4e1db43552860070061f156a98bb37b672b101ba6e3ddf30c",
            "1.0.2m": "8c6ff15ec6b319b50788f42c7abc2890c08ba5a1cdcd3810eb9092deada37b0f",
            "1.0.2n": "370babb75f278c39e0c50e8c4e7493bc0f18db6867478341a832a982fd15a8fe",
            "1.0.2o": "ec3f5c9714ba0fd45cb4e087301eb1336c317e0d20b575a125050470e8089e4d",
            "1.0.2p": "50a98e07b1a89eb8f6a99477f262df71c6fa7bef77df4dc83025a2845c827d00",
            "1.0.2q": "5744cfcbcec2b1b48629f7354203bc1e5e9b5466998bbccc5b5fcde3b18eb684",
            "1.0.2r": "ae51d08bba8a83958e894946f15303ff894d75c2b8bbd44a852b64e3fe11d0d6",
            "1.0.2s": "cabd5c9492825ce5bd23f3c3aeed6a97f8142f606d893df216411f07d1abab96",
            "1.1.0": "f5c69ff9ac1472c80b868efc1c1c0d8dcfc746d29ebe563de2365dd56dbd8c82",
            "1.1.0a": "c2e696e34296cde2c9ec5dcdad9e4f042cd703932591d395c389de488302442b",
            "1.1.0b": "a45de072bf9be4dea437230aaf036000f0e68c6a665931c57e76b5b036cef6f7",
            "1.1.0c": "fc436441a2e05752d31b4e46115eb89709a28aef96d4fe786abe92409b2fd6f5",
            "1.1.0d": "7d5ebb9e89756545c156ff9c13cf2aa6214193b010a468a3bc789c3c28fe60df",
            "1.1.0e": "57be8618979d80c910728cfc99369bf97b2a1abd8f366ab6ebdee8975ad3874c",
            "1.1.0f": "12f746f3f2493b2f39da7ecf63d7ee19c6ac9ec6a4fcd8c229da8a522cb12765",
            "1.1.0g": "de4d501267da39310905cb6dc8c6121f7a2cad45a7707f76df828fe1b85073af",
            "1.1.0h": "5835626cde9e99656585fc7aaa2302a73a7e1340bf8c14fd635a62c66802a517",
            "1.1.0i": "ebbfc844a8c8cc0ea5dc10b86c9ce97f401837f3fa08c17b2cdadc118253cf99",
            "1.1.0j": "31bec6c203ce1a8e93d5994f4ed304c63ccf07676118b6634edded12ad1b3246",
            "1.1.0k": "efa4965f4f773574d6cbda1cf874dbbe455ab1c0d4f906115f867d30444470b1",
            "1.1.1": "2836875a0f89c03d0fdf483941512613a50cfb421d6fd94b9f41d7279d586a3d",
            "1.1.1a": "fc20130f8b7cbd2fb918b2f14e2f429e109c31ddd0fb38fc5d71d9ffed3f9f41",
            "1.1.1b": "5c557b023230413dfb0756f3137a13e6d726838ccd1430888ad15bfb2b43ea4b",
            "1.1.1c": "f6fb3079ad15076154eda9413fed42877d668e7069d9b87396d0804fdb3f4c90",
        }
        try:
            url = "https://www.openssl.org/source/openssl-%s.tar.gz" % self.version
            tools.get(url, sha256=sha256[self.version])
        except ConanException:
            url = url.replace("https://www.openssl.org/source/",
                              "https://www.openssl.org/source/old/%s" % self._full_version.base)
            tools.get(url, sha256=sha256[self.version])
        extracted_folder = "openssl-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.capieng_dialog
        else:
            del self.options.fPIC

    def requirements(self):
        if not self.options.no_zlib:
            self.requires("zlib/1.2.11@conan/stable")

    @property
    def _target_prefix(self):
        if self._full_version < "1.1.0" and self.settings.build_type == "Debug":
            return "debug-"
        return ""

    @property
    def _target(self):
        target = "conan-%s-%s-%s-%s-%s" % (self.settings.build_type,
                                           self.settings.os,
                                           self.settings.arch,
                                           self.settings.compiler,
                                           self.settings.compiler.version)
        if self.settings.compiler == "Visual Studio":
            target = "VC-" + target  # VC- prefix is important as it's checked by Configure
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            target = "mingw-" + target
        return target

    @property
    def _targets(self):
        is_cygwin = self.settings.get_safe("os.subsystem") == "cygwin"
        is_1_0 = self._full_version < "1.1.0"
        return {
            "Linux-x86-clang": ("%slinux-generic32" % self._target_prefix) if is_1_0 else "linux-x86-clang",
            "Linux-x86_64-clang": ("%slinux-x86_64" % self._target_prefix) if is_1_0 else "linux-x86_64-clang",
            "Linux-x86-*": ("%slinux-generic32" % self._target_prefix) if is_1_0 else "linux-x86",
            "Linux-x86_64-*": "%slinux-x86_64" % self._target_prefix,
            "Linux-armv4-*": "linux-armv4",
            "Linux-armv4i-*": "linux-armv4",
            "Linux-armv5el-*": "linux-armv4",
            "Linux-armv5hf-*": "linux-armv4",
            "Linux-armv6-*": "linux-armv4",
            "Linux-armv7-*": "linux-armv4",
            "Linux-armv7hf-*": "linux-armv4",
            "Linux-armv7s-*": "linux-armv4",
            "Linux-armv7k-*": "linux-armv4",
            "Linux-armv8-*": "linux-aarch64",
            "Linux-armv8.3-*": "linux-aarch64",
            "Linux-armv8-32-*": "linux-arm64ilp32",
            "Linux-mips-*": "linux-mips32",
            "Linux-mips64-*": "linux-mips64",
            "Linux-ppc32-*": "linux-ppc32",
            "Linux-ppc32le-*": "linux-pcc32",
            "Linux-ppc32be-*": "linux-ppc32",
            "Linux-ppc64-*": "linux-ppc64",
            "Linux-ppc64le-*": "linux-ppc64le",
            "Linux-pcc64be-*": "linux-pcc64",
            "Linux-s390x-*": "linux64-s390x",
            "Linux-e2k-*": "linux-generic64",
            "Linux-sparc-*": "linux-sparcv8",
            "Linux-sparcv9-*": "linux64-sparcv9",
            "Linux-*-*": "linux-generic32",
            "Macos-x86-*": "%sdarwin-i386-cc" % self._target_prefix,
            "Macos-x86_64-*": "%sdarwin64-x86_64-cc" % self._target_prefix,
            "Macos-ppc32-*": "%sdarwin-ppc-cc" % self._target_prefix,
            "Macos-ppc32be-*": "%sdarwin-ppc-cc" % self._target_prefix,
            "Macos-ppc64-*": "darwin64-ppc-cc",
            "Macos-ppc64be-*": "darwin64-ppc-cc",
            "Macos-*-*": "darwin-common",
            "iOS": "ios-common",
            "watchOS": "ios-common",
            "tvOS": "ios-common",
            # Android targets are very broken, see https://github.com/openssl/openssl/issues/7398
            "Android-armv7-*": "linux-generic32",
            "Android-armv7hf-*": "linux-generic32",
            "Android-armv8-*": "linux-generic64",
            "Android-x86-*": "linux-generic32",
            "Android-x86_64-*": "linux-generic64",
            "Android-mips-*": "linux-generic32",
            "Android-mips64-*": "linux-generic64",
            "Android-*-*": "linux-generic32",
            "Windows-x86-gcc": "Cygwin-x86" if is_cygwin else "mingw",
            "Windows-x86_64-gcc": "Cygwin-x86_64" if is_cygwin else "mingw64",
            "Windows-*-gcc": "Cygwin-common" if is_cygwin else "mingw-common",
            "Windows-ia64-Visual Studio": "%sVC-WIN64I" % self._target_prefix,  # Itanium
            "Windows-x86-Visual Studio": "%sVC-WIN32" % self._target_prefix,
            "Windows-x86_64-Visual Studio": "%sVC-WIN64A" % self._target_prefix,
            "Windows-armv7-Visual Studio": "VC-WIN32-ARM",
            "Windows-armv8-Visual Studio": "VC-WIN64-ARM",
            "Windows-*-Visual Studio": "VC-noCE-common",
            "Windows-ia64-clang": "%sVC-WIN64I" % self._target_prefix,  # Itanium
            "Windows-x86-clang": "%sVC-WIN32" % self._target_prefix,
            "Windows-x86_64-clang": "%sVC-WIN64A" % self._target_prefix,
            "Windows-armv7-clang": "VC-WIN32-ARM",
            "Windows-armv8-clang": "VC-WIN64-ARM",
            "Windows-*-clang": "VC-noCE-common",
            "WindowsStore-x86-*": "VC-WIN32-UWP",
            "WindowsStore-x86_64-*": "VC-WIN64A-UWP",
            "WindowsStore-armv7-*": "VC-WIN32-ARM-UWP",
            "WindowsStore-armv8-*": "VC-WIN64-ARM-UWP",
            "WindowsStore-*-*": "VC-WIN32-ONECORE",
            "WindowsCE": "VC-CE",
            "SunOS-x86-gcc": "%ssolaris-x86-gcc" % self._target_prefix,
            "SunOS-x86_64-gcc": "%ssolaris64-x86_64-gcc" % self._target_prefix,
            "SunOS-sparc-gcc": "%ssolaris-sparcv8-gcc" % self._target_prefix,
            "SunOS-sparcv9-gcc": "solaris64-sparcv9-gcc",
            "SunOS-x86-suncc": "%ssolaris-x86-cc" % self._target_prefix,
            "SunOS-x86_64-suncc": "%ssolaris64-x86_64-cc" % self._target_prefix,
            "SunOS-sparc-suncc": "%ssolaris-sparcv8-cc" % self._target_prefix,
            "SunOS-sparcv9-suncc": "solaris64-sparcv9-cc",
            "SunOS-*-*": "solaris-common",
            "*BSD-x86-*": "BSD-x86",
            "*BSD-x86_64-*": "BSD-x86_64",
            "*BSD-ia64-*": "BSD-ia64",
            "*BSD-sparc-*": "BSD-sparcv8",
            "*BSD-sparcv9-*": "BSD-sparcv9",
            "*BSD-armv8-*": "BSD-generic64",
            "*BSD-mips64-*": "BSD-generic64",
            "*BSD-ppc64-*": "BSD-generic64",
            "*BSD-ppc64le-*": "BSD-generic64",
            "*BSD-ppc64be-*": "BSD-generic64",
            "AIX-ppc32-gcc": "aix-gcc",
            "AIX-ppc64-gcc": "aix64-gcc",
            "AIX-pcc32-*": "aix-cc",
            "AIX-ppc64-*": "aix64-cc",
            "AIX-*-*": "aix-common",
            "*BSD-*-*": "BSD-generic32",
            "Emscripten-*-*": "cc",
            "Neutrino-*-*": "BASE_unix",
        }

    @property
    def _ancestor_target(self):
        if "CONAN_OPENSSL_CONFIGURATION" in os.environ:
            return os.environ["CONAN_OPENSSL_CONFIGURATION"]
        query = "%s-%s-%s" % (self.settings.os, self.settings.arch, self.settings.compiler)
        ancestor = next((self._targets[i] for i in self._targets if fnmatch.fnmatch(query, i)), None)
        if not ancestor:
            raise ConanInvalidConfiguration("unsupported configuration: %s %s %s,"
                                            "please open an issue: "
                                            "https://github.com/conan-community/community/issues. "
                                            "alternatively, set the CONAN_OPENSSL_CONFIGURATION environment variable "
                                            "into your conan profile "
                                            "(list of configurations can be found by running './Configure --help')." %
                                            self.settings.os,
                                            self.settings.arch,
                                            self.settings.compiler)
        return ancestor

    def _tool(self, env_name, apple_name):
        if env_name in os.environ:
            return os.environ[env_name]
        if self.settings.compiler == "apple-clang":
            return getattr(tools.XCRun(self.settings), apple_name)
        return None

    @property
    def _configure_args(self):
        openssldir = self.options.openssldir if self.options.openssldir else os.path.join(self.package_folder, "res")
        prefix = tools.unix_path(self.package_folder) if self._win_bash else self.package_folder
        openssldir = tools.unix_path(openssldir) if self._win_bash else openssldir
        args = ['"%s"' % (self._target if self._full_version >= "1.1.0" else self._ancestor_target),
                "shared" if self.options.shared else "no-shared",
                "--prefix=%s" % prefix,
                "--openssldir=%s" % openssldir,
                "no-unit-test"]
        if self._full_version >= "1.1.1":
            args.append("PERL=%s" % self._perl)
        if self._full_version < "1.1.0" or self._full_version >= "1.1.1":
            args.append("no-tests")
        if self._full_version >= "1.1.0":
            args.append("--debug" if self.settings.build_type == "Debug" else "--release")

        if self.settings.os == "Android":
            args.append(" -D__ANDROID_API__=%s" % str(self.settings.os.api_level))  # see NOTES.ANDROID
        if self.settings.os == "Emscripten":
            args.append("-D__STDC_NO_ATOMICS__=1")
        if self.settings.os == "Windows":
            if self.options.capieng_dialog:
                args.append("-DOPENSSL_CAPIENG_DIALOG=1")
        else:
            args.append("-fPIC" if self.options.fPIC else "")

        if self._full_version < "1.1.0":
            env_build = AutoToolsBuildEnvironment(self)
            args.extend(env_build.flags)

        if "zlib" in self.deps_cpp_info.deps:
            zlib_info = self.deps_cpp_info["zlib"]
            include_path = zlib_info.include_paths[0]
            if self.settings.os == "Windows":
                lib_path = "%s/%s.lib" % (zlib_info.lib_paths[0], zlib_info.libs[0])
            else:
                lib_path = zlib_info.lib_paths[0]  # Just path, linux will find the right file
            if self.settings.os == "Windows":
                # clang-cl doesn't like backslashes in #define CFLAGS (builldinf.h -> cversion.c)
                include_path = include_path.replace('\\', '/')
                lib_path = lib_path.replace('\\', '/')
            args.extend(['--with-zlib-include="%s"' % include_path,
                         '--with-zlib-lib="%s"' % lib_path])

        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
            if activated and option_name not in ["fPIC", "openssldir", "capieng_dialog"]:
                self.output.info("activated option: %s" % option_name)
                args.append(option_name.replace("_", "-"))
        return args

    def _create_targets(self):
        config_template = """{targets} = (
    "{target}" => {{
        inherit_from => [ "{ancestor}" ],
        cflags => add("{cflags}"),
        cxxflags => add("{cxxflags}"),
        {defines}
        includes => add({includes}),
        lflags => add("{lflags}"),
        {cc}
        {cxx}
        {ar}
        {ranlib}
    }},
);
"""
        cflags = []
        if self.settings.compiler == "apple-clang":
            cflags.append("-arch %s" % tools.to_apple_arch(self.settings.arch))
            cflags.append("-isysroot %s" % tools.XCRun(self.settings).sdk_path)
            if self.settings.get_safe("os.version"):
                cflags.append(tools.apple_deployment_target_flag(self.settings.os,
                                                                 self.settings.os.version))

        env_build = AutoToolsBuildEnvironment(self)
        cflags.extend(env_build.flags)
        cxxflags = cflags[:]
        cxxflags.extend(env_build.cxx_flags)

        cc = self._tool("CC", "cc")
        cxx = self._tool("CXX", "cxx")
        ar = self._tool("AR", "ar")
        ranlib = self._tool("RANLIB", "ranlib")

        cc = 'cc => "%s",' % cc if cc else ""
        cxx = 'cxx => "%s",' % cxx if cxx else ""
        ar = 'ar => "%s",' % ar if ar else ""
        defines = " ".join(env_build.defines)
        defines = 'defines => add("%s"),' % defines if defines else ""
        ranlib = 'ranlib => "%s",' % ranlib if ranlib else ""
        targets = "my %targets" if self._full_version >= "1.1.1" else "%targets"
        includes = ", ".join(['"%s"' % include for include in env_build.include_paths])
        if self.settings.os == "Windows":
            includes = includes.replace('\\', '/') # OpenSSL doesn't like backslashes

        config = config_template.format(targets=targets,
                                        target=self._target,
                                        ancestor=self._ancestor_target,
                                        cc=cc,
                                        cxx=cxx,
                                        ar=ar,
                                        ranlib=ranlib,
                                        cflags=" ".join(cflags),
                                        cxxflags=" ".join(cxxflags),
                                        defines=defines,
                                        includes=includes,
                                        lflags=" ".join(env_build.link_flags))
        self.output.info("using target: %s -> %s" % (self._target, self._ancestor_target))
        self.output.info(config)

        tools.save(os.path.join(self._source_subfolder, "Configurations", "20-conan.conf"), config)

    def _run_make(self, targets=None, makefile=None, parallel=True):
        command = [self._make_program]
        if makefile:
            command.extend(["-f", makefile])
        if targets:
            command.extend(targets)
        if self.settings.compiler != "Visual Studio":
            # workaround for random error: size too large (archive member extends past the end of the file)
            # /Library/Developer/CommandLineTools/usr/bin/ar: internal ranlib command failed
            if self.settings.os == "Macos" and self._full_version < "1.1.0":
                parallel = False
            command.append(("-j%s" % tools.cpu_count()) if parallel else "-j1")
        self.run(" ".join(command), win_bash=self._win_bash)

    @property
    def _perl(self):
        if tools.os_info.is_windows:
            # enforce strawberry perl, otherwise wrong perl could be used (from Git bash, MSYS, etc.)
            return os.path.join(self.deps_cpp_info["strawberryperl"].rootpath, "perl", "bin", "perl.exe")
        return tools.which("perl") or "perl"

    def _make(self):
        with tools.chdir(self._source_subfolder):
            # workaround for MinGW (https://github.com/openssl/openssl/issues/7653)
            if not os.path.isdir(os.path.join(self.package_folder, "bin")):
                os.makedirs(os.path.join(self.package_folder, "bin"))
            args = " ".join(self._configure_args)
            self.output.info(self._configure_args)

            self.run('{perl} ./Configure {args}'.format(perl=self._perl, args=args), win_bash=self._win_bash)

            self._patch_install_name()

            if self.settings.compiler == "Visual Studio" and self._full_version < "1.1.0":
                if not self.options.no_asm and self.settings.arch == "x86":
                    self.run(r"ms\do_nasm")
                else:
                    self.run(r"ms\do_ms" if self.settings.arch == "x86" else r"ms\do_win64a")
                makefile = r"ms\ntdll.mak" if self.options.shared else r"ms\nt.mak"

                self._replace_runtime_in_file(os.path.join("ms", "nt.mak"))
                self._replace_runtime_in_file(os.path.join("ms", "ntdll.mak"))
                if self.settings.arch == "x86":
                    tools.replace_in_file(os.path.join("ms", "nt.mak"), "-WX", "")
                    tools.replace_in_file(os.path.join("ms", "ntdll.mak"), "-WX", "")

                self._run_make(makefile=makefile)
                self._run_make(makefile=makefile, targets=["install"], parallel=False)
            else:
                self._run_make()
                self._run_make(targets=["install_sw"], parallel=False)

    def build(self):
        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            with tools.environment_append({"PERL": self._perl}):
                if self._full_version >= "1.1.0":
                    self._create_targets()
                self._make()

    @property
    def _win_bash(self):
        return tools.os_info.is_windows and self.settings.compiler != "Visual Studio"

    @property
    def _make_program(self):
        if self.settings.compiler == "Visual Studio":
            return "nmake"
        make_program = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which('mingw32-make'))
        make_program = tools.unix_path(make_program) if tools.os_info.is_windows else make_program
        return make_program

    def _patch_install_name(self):
        if self.settings.os == "Macos" and self.options.shared:
            old_str = '-install_name $(INSTALLTOP)/$(LIBDIR)/'
            new_str = '-install_name '

            makefile = "Makefile" if self._full_version >= "1.1.1" else "Makefile.shared"
            tools.replace_in_file(makefile, old_str, new_str, strict=self.in_local_cache)

    def _replace_runtime_in_file(self, filename):
        for e in ["MDd", "MTd", "MD", "MT"]:
            tools.replace_in_file(filename, "/%s " % e, "/%s " % self.settings.compiler.runtime, strict=False)

    def package(self):
        self.copy(src=self._source_subfolder, pattern="*LICENSE", dst="licenses")
        for root, _, files in os.walk(self.package_folder):
            for filename in files:
                if fnmatch.fnmatch(filename, "*.pdb"):
                    os.unlink(os.path.join(self.package_folder, root, filename))
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            if self.settings.build_type == 'Debug' and self._full_version >= "1.1.0":
                with tools.chdir(os.path.join(self.package_folder, 'lib')):
                    os.rename('libssl.lib', 'libssld.lib')
                    os.rename('libcrypto.lib', 'libcryptod.lib')
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self._full_version < "1.1.0":
                self.cpp_info.libs = ["ssleay32", "libeay32"]
            else:
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs = ['libssld', 'libcryptod']
                else:
                    self.cpp_info.libs = ['libssl', 'libcrypto']
        else:
            self.cpp_info.libs = ["ssl", "crypto"]
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(["crypt32", "msi", "ws2_32", "advapi32", "user32"])
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(["dl", "pthread"])
