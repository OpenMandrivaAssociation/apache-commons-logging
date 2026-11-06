Name:		apache-commons-logging
Version:	1.4.0
Release:	1
Summary:	Apache Commons Logging
Group:		Development/Java
License:	ASL 2.0
URL:		https://commons.apache.org/proper/commons-logging/
Source0:	https://archive.apache.org/dist/commons/logging/source/commons-logging-%{version}-src.tar.gz

BuildArch:	noarch
BuildRequires:	mvn(org.apache.commons:commons-parent:pom::)
# Optional adapters. builddep does not emit optional dependencies.
BuildRequires:	mvn(org.slf4j:slf4j-api)
BuildRequires:	mvn(log4j:log4j)
BuildRequires:	mvn(javax.servlet:javax.servlet-api)
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name commons-logging --link %{name} --alias org.apache.commons:commons-logging --alias apache:commons-logging

%description
Apache Commons Logging is a thin adapter from application code to
another logging system. 1.4.0 needs Java 8. The SLF4J and Log4j 1.2
adapters are compiled against the system jars. Avalon, LogKit, Log4j 2,
and Jakarta Servlet are not packaged, so those adapters are left out.
Tests are skipped.

%prep
%setup -q -n commons-logging-%{version}-src
# Ship one jar. The api and adapters classifiers and the test jar are extra artifacts.
# Avalon, LogKit, Log4j 2, and Jakarta Servlet have no system jar.
# Log4j 1.2 is the packaged log4j:log4j jar, not the Log4j 2 bridge.
python - <<'PY'
import re
from pathlib import Path
path = Path("pom.xml")
text = path.read_text()
for exec_id in ("create-test-jar", "create-api-jar", "create-adapters-jar"):
    pattern = (
        r"[ \t]*<execution>\s*(?:<!--.*?-->\s*)*<id>"
        + exec_id
        + r"</id>.*?</execution>\n"
    )
    text, count = re.subn(pattern, "", text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"{exec_id} removed {count}")
empty = "        <executions>\n        </executions>\n"
if text.count(empty) != 1:
    raise SystemExit(f"empty executions count {text.count(empty)}")
text = text.replace(empty, "", 1)
log4j = """    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-1.2-api</artifactId>
      <version>${log4j2.version}</version>
      <optional>true</optional>
    </dependency>
"""
log4j_new = """    <dependency>
      <groupId>log4j</groupId>
      <artifactId>log4j</artifactId>
      <version>1.2.17</version>
      <optional>true</optional>
    </dependency>
"""
if log4j not in text:
    raise SystemExit("log4j 1.2 bridge dependency not found")
text = text.replace(log4j, log4j_new, 1)
drops = (
"""    <dependency>
      <groupId>avalon-framework</groupId>
      <artifactId>avalon-framework</artifactId>
      <version>4.1.5</version>
      <optional>true</optional>
    </dependency>
""",
"""    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-api</artifactId>
      <version>${log4j2.version}</version>
      <optional>true</optional>
    </dependency>
""",
"""    <dependency>
      <groupId>logkit</groupId>
      <artifactId>logkit</artifactId>
      <version>2.0</version>
      <optional>true</optional>
    </dependency>
""",
"""    <dependency>
      <groupId>jakarta.servlet</groupId>
      <artifactId>jakarta.servlet-api</artifactId>
      <version>${jakarta.servlet-api.version}</version>
      <scope>provided</scope>
      <optional>true</optional>
    </dependency>
""",
)
for block in drops:
    if block not in text:
        raise SystemExit("dependency block not found")
    text = text.replace(block, "", 1)
if "<groupId>log4j</groupId>" not in text:
    raise SystemExit("log4j dependency missing")
if "<groupId>avalon-framework</groupId>" in text or "<groupId>logkit</groupId>" in text:
    raise SystemExit("removed logging dependency still present")
if "<groupId>jakarta.servlet</groupId>" in text:
    raise SystemExit("jakarta servlet dependency still present")
path.write_text(text)
for name in (
    "src/main/java/org/apache/commons/logging/impl/AvalonLogger.java",
    "src/main/java/org/apache/commons/logging/impl/LogKitLogger.java",
    "src/main/java/org/apache/commons/logging/impl/Log4jApiLogFactory.java",
    "src/main/java/org/apache/commons/logging/jakarta/ServletContextCleaner.java",
):
    file = Path(name)
    if not file.is_file():
        raise SystemExit(f"missing {name}")
    file.unlink()
PY

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt PROPOSAL.html RELEASE-NOTES.txt
