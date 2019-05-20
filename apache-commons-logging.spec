%global base_name  logging
%global short_name commons-%{base_name}

Name:           apache-%{short_name}
Version:        1.2
Release:        1
Summary:        Apache Commons Logging
License:        ASL 2.0
URL:            http://commons.apache.org/%{base_name}
Source0:        http://www.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
Source1:        http://mirrors.ibiblio.org/pub/mirrors/maven2/%{short_name}/%{short_name}-api/1.1/%{short_name}-api-1.1.pom

BuildRequires:	jdk-current
BuildRequires:	javapackages-local

BuildArch:      noarch


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

%description    javadoc
%{summary}.

# -----------------------------------------------------------------------------

%prep
%autosetup -p1 -n %{short_name}-%{version}-src
# avalon-framework requires commons-logging to build -- let's avoid
# the circular dependency. Avalon is dead upstream and hasn't seen
# a release in 12+ years anyway.
rm -f src/main/java/org/apache/commons/logging/impl/AvalonLogger.java
# And while at it, let's be progressive here to reduce dependency
# bloat.
# JDK 1.3 is obsolete.
rm -f src/main/java/org/apache/commons/logging/impl/Jdk13LumberjackLogger.java
# Log4J 1.x (as implemented by commons-logging) and LogKit
# are rather obsolete given we have java.logging these days.
rm -f src/main/java/org/apache/commons/logging/impl/Log4JLogger.java
rm -f src/main/java/org/apache/commons/logging/impl/LogKitLogger.java

# Fix some javadoc comments
find src -name "*.java" |xargs sed -i -e 's,<tt>,<code>,g;s,</tt>,</code>,g'

%build
buildjar() {
	if ! [ -e module-info.java ]; then
		MODULE="$1"
		shift
		echo "module $MODULE {" >module-info.java
		find . -name "*.java" |xargs grep ^package |sed -e 's,^.*package ,,;s,\;.*,,' -e 's/^[[:space:]]*//g' -e 's/[[:space:]]*\$//g' |sort |uniq |while read e; do
			echo "  exports $e;" >>module-info.java
		done
		for i in "$@"; do
			echo "	requires $i;" >>module-info.java
		done
		echo '}' >>module-info.java
	fi
	find . -name "*.java" |xargs javac -p %{_javadir}/modules
	find . -name "*.class" -o -name "*.properties" |xargs jar cf $MODULE-%{version}.jar
	jar i $MODULE-%{version}.jar
	# Javadoc for javax.servlet is broken and in need of compile
	# fixes
	javadoc -d docs -sourcepath . -p %{_javadir}/modules $MODULE
}
cd src/main/java
buildjar org.apache.commons.logging java.logging javax.servlet

%install
mkdir -p %{buildroot}%{_javadir}/modules %{buildroot}%{_mavenpomdir} %{buildroot}%{_javadocdir}
cp src/main/java/org.apache.commons.logging-%{version}.jar %{buildroot}%{_javadir}/modules
ln -s modules/org.apache.commons.logging-%{version}.jar %{buildroot}%{_javadir}/
ln -s modules/org.apache.commons.logging-%{version}.jar %{buildroot}%{_javadir}/org.apache.commons.logging.jar
ln -s modules/org.apache.commons.logging-%{version}.jar %{buildroot}%{_javadir}/commons-logging-api.jar
ln -s modules/org.apache.commons.logging-%{version}.jar %{buildroot}%{_javadir}/commons-logging-adapters.jar
sed -e 's,1\.1,%{version},g' %{S:1} >%{buildroot}%{_mavenpomdir}/%{short_name}-api-%{version}.pom
%add_maven_depmap %{short_name}-api-%{version}.pom org.apache.commons.logging-%{version}.jar
cp -a src/main/java/docs %{buildroot}%{_javadocdir}/%{name}

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt
%doc PROPOSAL.html RELEASE-NOTES.txt
%{_javadir}/*.jar
%{_javadir}/modules/*.jar

%files javadoc
%{_javadocdir}/%{name}
