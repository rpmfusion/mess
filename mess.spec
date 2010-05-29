# the debug build is disabled by default, please use --with debug to override
%bcond_with debug

%global baseversion 138

Name:           mess
Version:        0.%{baseversion}
Release:        2%{?dist}
Summary:        Multiple Emulator Super System

Group:          Applications/Emulators
#Files in src/lib/util and src/osd (except src/osd/sdl) are BSD
License:        MAME License
URL:            http://www.mess.org/
Source0:        http://www.aarongiles.com/mirror/releases/mame0%{baseversion}s.exe
Source1:        http://www.mess.org/files/%{name}0%{baseversion}s.zip
Source2:        ctrlr.rar
#ui.bdc generated from ui.bdf
#Source2:        ui.bdc
Patch0:         %{name}-fortify.patch
Patch1:         %{name}-verbosebuild.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  expat-devel
BuildRequires:  GConf2-devel
BuildRequires:  gtk2-devel
BuildRequires:  p7zip
BuildRequires:  SDL-devel
BuildRequires:  unrar
BuildRequires:  zlib-devel

Provides:       sdlmess = 0%{baseversion}-%{release}
Obsoletes:      sdlmess < 0136-2

%description
MESS is an acronym that stands for Multiple Emulator Super System. MESS will
more or less faithfully reproduce computer and console systems on a PC.

MESS emulates the hardware of the systems and sometimes utilizes ROM images to
load programs and games.  Therefore, these systems are NOT simulations, but
the actual emulations of the hardware.

%package tools
Summary:        Tools used for the MESS package
Group:          Applications/Emulators
Requires:       %{name} = %{version}-%{release}

Provides:       sdlmess-tools = 0%{baseversion}-%{release}
Obsoletes:      sdlmess-tools < 0136-2

%description tools
%{summary}.

%package data
Summary:        Data files used for the MESS package
Group:          Applications/Emulators
Requires:       %{name} = %{version}-%{release}

Provides:       sdlmess-data = 0%{baseversion}-%{release}
Obsoletes:      sdlmess-data < 0136-2

BuildArch:      noarch

%description data
%{summary}.


%prep
%setup -qcT
7za x %{SOURCE0}
find . -type f -not -name uismall.png -exec sed -i 's/\r//' {} \;
unzip -o %{SOURCE1}
%patch0 -p1 -b .fortify
%patch1 -p1 -b .verbosebuild

# Remove windows-specific documentation
rm -fr docs/win*

# Move the imgtool documentation to the top dir for better visibility
mv docs/imgtool.txt .

# Fix permissions
chmod 644 docs/config.txt docs/credits.htm docs/license.txt docs/mame.txt docs/newvideo.txt
find src/mess -type f \( -name \*.h -or -name \*.c \) -exec chmod 644 {} \;
chmod 644 src/mame/machine/snescx4.h

# Fix newvideo.txt encoding
pushd docs
/usr/bin/iconv -f cp1250 -t utf-8 newvideo.txt > newvideo.txt.conv
/bin/mv -f newvideo.txt.conv newvideo.txt
popd

# Create ini file
cat > %{name}.ini << EOF
# Define multi-user paths
artpath            %{_datadir}/%{name}/artwork;%{_datadir}/%{name}/effects
ctrlrpath          %{_datadir}/%{name}/ctrlr
fontpath           %{_datadir}/%{name}/fonts
hashpath           %{_datadir}/%{name}/hash
rompath            %{_datadir}/%{name}/roms
samplepath         %{_datadir}/%{name}/samples
cheatpath          %{_datadir}/%{name}/cheats

# Allow user to override ini settings
inipath            \$HOME/.%{name}/ini;%{_sysconfdir}/%{name}

# Set paths for local storage
cfg_directory      \$HOME/.%{name}/cfg
comment_directory  \$HOME/.%{name}/comments
diff_directory     \$HOME/.%{name}/diff
input_directory    \$HOME/.%{name}/inp
memcard_directory  \$HOME/.%{name}/memcard
nvram_directory    \$HOME/.%{name}/nvram
snapshot_directory \$HOME/.%{name}/snap
state_directory    \$HOME/.%{name}/sta

# Fedora custom defaults
video              opengl
autosave           1
joystick           1
EOF


%build
%if %{with debug}
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 SUFFIX64="" \
    OPT_FLAGS='%{optflags} -DINI_PATH="\"%{_sysconfdir}/%{name};\""' DEBUG=1 all TARGET=mess
%else
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 SUFFIX64="" \
    OPT_FLAGS='%{optflags} -DINI_PATH="\"%{_sysconfdir}/%{name};\""' all TARGET=mess
%endif


%install
rm -rf %{buildroot}

# create directories
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/%{name}/artwork
install -d %{buildroot}%{_datadir}/%{name}/roms
install -d %{buildroot}%{_datadir}/%{name}/ctrlr
install -d %{buildroot}%{_datadir}/%{name}/fonts
install -d %{buildroot}%{_datadir}/%{name}/hash
install -d %{buildroot}%{_datadir}/%{name}/samples
install -d %{buildroot}%{_datadir}/%{name}/software
install -d %{buildroot}%{_datadir}/%{name}/cheats
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/cfg
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/comments
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/diff
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/ini
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/inp
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/memcard
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/nvram
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/sta
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/snap

# Install binaries and config files
%if %{with debug}
install -pm 755 %{name}d %{buildroot}%{_bindir}
%else
install -pm 755 %{name} %{buildroot}%{_bindir}
%endif
install -pm 755 castool dat2html imgtool messtest %{buildroot}%{_bindir}
install -pm 644 sysinfo.dat %{buildroot}%{_datadir}/%{name}
install -pm 644 artwork/* %{buildroot}%{_datadir}/%{name}/artwork
#install -pm 644 ui.bdf %{SOURCE2} %{buildroot}%{_datadir}/%{name}/fonts
install -pm 644 hash/* %{buildroot}%{_datadir}/%{name}/hash
install -pm 644 %{name}.ini %{buildroot}%{_sysconfdir}/%{name}

# Install controller files
unrar x %{SOURCE2} %{buildroot}%{_datadir}/%{name}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc *.txt docs/*
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.ini
%dir %{_sysconfdir}/%{name}
%if %{with debug}
%{_bindir}/%{name}d
%else
%{_bindir}/%{name}
%endif
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/artwork
%dir %{_datadir}/%{name}/roms
%dir %{_datadir}/%{name}/ctrlr
%{_datadir}/%{name}/fonts
%dir %{_datadir}/%{name}/hash
%dir %{_datadir}/%{name}/samples
%dir %{_datadir}/%{name}/software
%dir %{_datadir}/%{name}/cheats
%{_sysconfdir}/skel/.%{name}

%files tools
%defattr(-,root,root,-)
%doc imgtool.txt
%{_bindir}/castool
%{_bindir}/dat2html
%{_bindir}/imgtool
%{_bindir}/messtest

%files data
%defattr(-,root,root,-)
%{_datadir}/%{name}/sysinfo.dat
%{_datadir}/%{name}/artwork/*
%{_datadir}/%{name}/ctrlr/*
%{_datadir}/%{name}/hash/*


%changelog
* Mon May 24 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138-2
- Binary is MAME-licensed, BSD only applies to the source

* Sun May 23 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138-1
- Initial package based on mame and sdlmess
