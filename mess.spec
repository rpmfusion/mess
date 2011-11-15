# the debug build is disabled by default, please use --with debug to override
%bcond_with debug

%global baseversion 144
%global snapshot 0

Name:           mess
Version:        0.%{baseversion}
Release:        1%{?dist}
Summary:        Multiple Emulator Super System

#Files in src/lib/util and src/osd (except src/osd/sdl) are BSD
License:        MAME License
URL:            http://www.mess.org/
%if 0%{?snapshot}
Source0:        mess-snapshot.tar.xz
%else
#Available here:
#http://www.mess.org/downloads
Source0:        %{name}0%{baseversion}s.zip
%endif
Source1:        ctrlr.rar
Patch0:         %{name}-fortify.patch
Patch1:         %{name}-verbosebuild.patch

BuildRequires:  expat-devel
BuildRequires:  GConf2-devel
BuildRequires:  gtk2-devel
BuildRequires:  SDL_ttf-devel
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
%if 0%{?snapshot}
%setup -qn %{name}
%else
%setup -qc
# Fix end-of-line encoding, but don't ruin binary files
find . -type f -not -name \*.png -not -name \*.zip -exec sed -i 's/\r//' {} \;
%endif
%patch0 -p1 -b .fortify
%patch1 -p1 -b .verbosebuild

# Remove windows-specific documentation
rm -fr docs/win*

# Move the imgtool documentation to the top dir for better visibility
mv docs/imgtool.txt .

# Fix whatsnew.txt encoding
iconv -f cp1252 -t utf-8 whatsnew.txt > whatsnew.txt.conv && mv -f whatsnew.txt.conv whatsnew.txt

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
EOF


%build
#these flags are already included in the Makefile
RPM_OPT_FLAGS=$(echo $RPM_OPT_FLAGS | sed -e s/"-O2 -g -pipe -Wall "//)

%if %{with debug}
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 SUFFIX64="" \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/%{name};\"'" DEBUG=1 all TARGET=mess
%else
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 SUFFIX64="" \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/%{name};\"'" all TARGET=mess
%endif


%install
rm -rf $RPM_BUILD_ROOT

# create directories
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/artwork
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/roms
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/ctrlr
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/fonts
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/hash
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/samples
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/software
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/cheats
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/cfg
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/comments
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/diff
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/ini
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/inp
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/memcard
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/nvram
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/sta
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/snap

# Install binaries and config files
%if %{with debug}
install -pm 755 %{name}d $RPM_BUILD_ROOT%{_bindir}
%else
install -pm 755 %{name} $RPM_BUILD_ROOT%{_bindir}
%endif
install -pm 755 castool dat2html imgtool $RPM_BUILD_ROOT%{_bindir}
install -pm 644 sysinfo.dat $RPM_BUILD_ROOT%{_datadir}/%{name}
install -pm 644 artwork/* $RPM_BUILD_ROOT%{_datadir}/%{name}/artwork
install -pm 644 hash/* $RPM_BUILD_ROOT%{_datadir}/%{name}/hash
install -pm 644 %{name}.ini $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

# Install controller files
unrar x %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/%{name}


%files
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
%doc imgtool.txt
%{_bindir}/castool
%{_bindir}/dat2html
%{_bindir}/imgtool

%files data
%{_datadir}/%{name}/sysinfo.dat
%{_datadir}/%{name}/artwork/*
%{_datadir}/%{name}/ctrlr/*
%{_datadir}/%{name}/hash/*


%changelog
* Tue Nov 15 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.144-1
- Updated to 0.144
- Updated the Source0 URL comment
- Fixed whatsnew.txt encoding (cp1252 → utf-8)
- Dropped obsolete Group, Buildroot, %%clean and %%defattr

* Wed Jun 29 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143-1
- Updated to 0.143
- Updated the verbosebuild patch
- MAME source is not needed anymore
- Dropped p7zip from BuildRequires

* Mon Apr 04 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.142-1
- Updated to 0.142
- Provided an easy way to build a SVN snapshot
- Filtered out redundant $RPM_OPT_FLAGS
- No longer enable joystick by default
- Re-enabled the fortify patch
- Delete mame hash files
- Dropped messtest

* Fri Jan 14 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.141-1
- Updated to 0.141
- Temporarily dropped the fortify patch
- Added SDL_ttf-devel to BuildRequires, removed explicit SDL-devel

* Mon Nov 01 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.140-1
- Updated to 0.140
- Updated the verbosebuild patch

* Sun Aug 01 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.139-1
- Updated to 0.139
- Updated the verbosebuild patch

* Mon May 24 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138-2
- Binary is MAME-licensed, BSD only applies to the source

* Sun May 23 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138-1
- Initial package based on mame and sdlmess
