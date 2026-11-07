FROM --platform={{platform}} public.ecr.aws/d3j8x8q7/olympus-base-go:latest
RUN curl -fsSL -o /tmp/go.tgz https://dl.google.com/go/go{{toolchain_version}}.linux-amd64.tar.gz \
    && echo "{{go_sha256}}  /tmp/go.tgz" | sha256sum -c - \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf /tmp/go.tgz \
    && rm /tmp/go.tgz \
    && go version
ENV PATH=/usr/local/go/bin:/opt/go/bin:/usr/local/bin:/usr/bin:/bin
ENV GOTOOLCHAIN=local GOWORK=off GOCACHE=/opt/adapter-gocache GOPATH=/opt/go
ENV GOFLAGS="-buildvcs=false -trimpath"
WORKDIR /app
COPY . .
RUN go mod download \
    && {{build_commands}}
RUN mkdir -p /opt/adapter-gocache \
    && find /app /opt/go -type d ! -perm -005 -exec chmod a+rx {} + \
    && find /app /opt/go -type f ! -perm -004 -exec chmod a+r {} + \
    && chmod -R a+rwX /opt/adapter-gocache \
    && git config --system --add safe.directory /app
RUN {{development_install}}
CMD ["/bin/bash"]
