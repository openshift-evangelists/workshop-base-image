FROM centos/s2i-base-centos7:latest

# Install additional common utilities.

RUN HOME=/root && \
    INSTALL_PKGS="nano" && \
    yum install -y centos-release-scl && \
    yum -y --setopt=tsflags=nodocs install --enablerepo=centosplus $INSTALL_PKGS && \
    rpm -V $INSTALL_PKGS && \
    yum -y clean all --enablerepo='*'

# Install OpenShift client.

ENV OC_VERSION=3.9.31
RUN curl -s -o /tmp/oc.tar.gz "https://mirror.openshift.com/pub/openshift-v3/clients/$OC_VERSION/linux/oc.tar.gz" && \
    tar -C /usr/local/bin -zxvf /tmp/oc.tar.gz oc && \
    rm /tmp/oc.tar.gz && \
    curl -sL -o /usr/local/bin/odo https://github.com/redhat-developer/odo/releases/download/v0.0.10/odo-linux-amd64 && \
    chmod +x /usr/local/bin/odo

# Common environment variables.

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    PIP_NO_CACHE_DIR=off

# Install Supervisor and Butterfly using system Python 2.7.

RUN HOME=/opt/terminal && \
    mkdir -p /opt/terminal && \
    curl -s -o /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    /usr/bin/python /tmp/get-pip.py --user && \
    rm -f /tmp/get-pip.py && \
    $HOME/.local/bin/pip install --no-cache-dir --user virtualenv && \
    $HOME/.local/bin/virtualenv /opt/terminal && \
    source /opt/terminal/bin/activate && \
    pip install supervisor==3.3.4 && \
    mkdir -p /opt/app-root/etc && \
    pip install https://github.com/GrahamDumpleton/butterfly/archive/uri-root-path.zip && \
    rm /opt/app-root/etc/scl_enable

ENV BASH_ENV=/opt/terminal/etc/profile \
    ENV=/opt/terminal/etc/profile \
    PROMPT_COMMAND=". /opt/terminal/etc/profile"

COPY scripts/. /opt/terminal/bin/
COPY configs/. /opt/terminal/etc/

COPY builder/. /usr/libexec/s2i/

RUN echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
    chmod g+w /etc/passwd

RUN touch /opt/terminal/etc/envvars && \
    chown -R 1001:0 /opt/terminal/etc/envvars && \
    chmod g+w /opt/terminal/etc/envvars

RUN mkdir -p /opt/app-root/etc/init.d && \
    mkdir -p /opt/app-root/etc/profile.d && \
    chown -R 1001:0 /opt/app-root && \
    fix-permissions /opt/app-root

LABEL io.k8s.display-name="Terminal (Base Image)." \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="builder,butterfly" \
      io.openshift.s2i.scripts-url=image:///usr/libexec/s2i

EXPOSE 8080

USER 1001

CMD [ "/usr/libexec/s2i/run" ]
