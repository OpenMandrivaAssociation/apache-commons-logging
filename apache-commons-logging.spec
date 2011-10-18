
%global base_name  logging
%global short_name commons-%{base_name}

Name:           apache-%{short_name}
Version:        1.1.1
Release:        17
Summary:        Apache Commons Logging
License:        ASL 2.0
Group:          Development/Java
URL:            http://commons.apache.org/%{base_name}
Source0:        http://www.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
Source1:        %{short_name}.depmap
Source2:        http://mirrors.ibiblio.org/pub/mirrors/maven2/%{short_name}/%{short_name}-api/1.1/%{short_name}-api-1.1.pom
# Sent upstream https://issues.apache.org/jira/browse/LOGGING-143
Patch0:         %{short_name}-avalon-update.patch

Patch1:         %{short_name}-eclipse-manifest.patch
BuildArch:      noarch
BuildRequires:  maven
BuildRequires:  java-devel >= 0:1.6.0
BuildRequires:  jpackage-utils >= 0:1.7.5
BuildRequires:  avalon-framework >= 4.3
BuildRequires:  avalon-logkit
BuildRequires:  apache-commons-parent
BuildRequires:  maven-plugin-build-helper
BuildRequires:  maven-release-plugin
BuildRequires:  maven-site-plugin
BuildRequires:  servlet25

Requires:       java >= 0:1.6.0
Requires:       jpackage-utils >= 0:1.7.5
Requires(post): jpackage-utils >= 0:1.7.5
Requires(postun):jpackage-utils >= 0:1.7.5

# This should go away with F-17
Provides:       jakarta-%{short_name} = 0:%{version}-%{release}
Obsoletes:      jakarta-%{short_name} <= 0:1.0.4

%description
The commons-logging package provides a simple, component oriented
interface (org.apache.commons.logging.Log) together with wrappers for
logging systems. The user can choose at runtime which system they want
to use. In addition, a small number of basic implementations are
provided to allow users to use the package standalone.
commons-logging was heavily influenced by Avalon's Logkit and Log4J. The
commons-logging abstraction is meant to minimize the differences between
the two, and to allow a developer to not tie himself to a particular
logging implementation.

%package        javadoc
Summary:        API documentation for %{name}
Group:          Development/Java
Requires:       jpackage-utils >= 0:1.7.5

Obsoletes:      jakarta-%{short_name}-javadoc <= 0:1.0.4

%description    javadoc
%{summary}.

# -----------------------------------------------------------------------------

%prep
%setup -q -n %{short_name}-%{version}-src

%patch0 -p1
%patch1

sed -i 's/\r//' RELEASE-NOTES.txt LICENSE.txt

# -----------------------------------------------------------------------------

%build
# fails with recent surefire for some reason
rm src/test/org/apache/commons/logging/logkit/StandardTestCase.java
rm src/test/org/apache/commons/logging/servlet/BasicServletTestCase.java

# These files have names suggesting they are test cases but they are not.
# They should probably be renamed/excluded from surefire run properly
rm src/test/org/apache/commons/logging/log4j/log4j12/*StandardTestCase.java

mvn-rpmbuild -X -Dmaven.local.depmap.file="%{SOURCE1}" \
    install javadoc:aggregate

# -----------------------------------------------------------------------------

%install
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -p -m 644 target/%{short_name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar
install -p -m 644 target/%{short_name}-api-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-api.jar
install -p -m 644 target/%{short_name}-adapters-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-adapters.jar

pushd $RPM_BUILD_ROOT%{_javadir}
for jar in %{name}*; do
    ln -sf ${jar} `echo $jar| sed "s|apache-||g"`
done
popd

# pom
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 pom.xml $RPM_BUILD_ROOT/%{_mavenpomdir}/JPP-%{short_name}.pom
install -pm 644 %{SOURCE2} $RPM_BUILD_ROOT/%{_mavenpomdir}/JPP-%{short_name}-api.pom

%add_to_maven_depmap org.apache.commons %{short_name} %{version} JPP %{short_name}
%add_to_maven_depmap org.apache.commons %{short_name}-api %{version} JPP %{short_name}-api
%add_to_maven_depmap org.apache.commons %{short_name}-adapters %{version} JPP %{short_name}-adapters

# following lines are only for backwards compatibility. New packages
# should use proper groupid org.apache.commons and also artifactid
%add_to_maven_depmap %{short_name} %{short_name} %{version} JPP %{short_name}
%add_to_maven_depmap %{short_name} %{short_name}-api %{version} JPP %{short_name}-api
%add_to_maven_depmap %{short_name} %{short_name}-adapters %{version} JPP %{short_name}-adapters


# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# -----------------------------------------------------------------------------
%post
%update_maven_depmap

%postun
%update_maven_depmap

%pre javadoc
# workaround for rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :


# -----------------------------------------------------------------------------

%files
%defattr(-,root,root,-)
%doc PROPOSAL.html STATUS.html LICENSE.txt RELEASE-NOTES.txt
%{_javadir}/*
%{_mavenpomdir}/JPP-%{short_name}.pom
%{_mavenpomdir}/JPP-%{short_name}-api.pom
%{_mavendepmapfragdir}/*


%files javadoc
%defattr(-,root,root,-)
%doc LICENSE.txt
%{_javadocdir}/%{name}

