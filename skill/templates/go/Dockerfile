FROM public.ecr.aws/d3j8x8q7/olympus-base-go:latest

# go.mod needs Go {{toolchain_version}} and the base image ships another Go release (GOTOOLCHAIN=local, so go
# never switches toolchains on its own). Install the Go {{toolchain_version}} release archive in its place,
# checked against its published SHA-256, so every go command uses {{toolchain_version}} and nothing downloads
# a toolchain later.
RUN curl -fsSL -o /tmp/go.tgz https://dl.google.com/go/go{{toolchain_version}}.linux-amd64.tar.gz \
    && echo "{{go_sha256}}  /tmp/go.tgz" | sha256sum -c - \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf /tmp/go.tgz \
    && rm /tmp/go.tgz \
    && go version
ENV PATH=/usr/local/go/bin:/opt/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV GOTOOLCHAIN=local GOWORK=off GOCACHE=/opt/adapter-gocache GOPATH=/opt/go
ENV GOFLAGS="-buildvcs=false -trimpath"
WORKDIR /app
COPY . .
RUN go mod download \
    && {{build_commands}}
RUN {{development_install}}
RUN mkdir -p /opt/adapter-gocache /opt/go/pkg/mod/cache \
    && chmod -R a+rX /opt/go \
    && chmod -R a+rwX /app /opt/adapter-gocache /opt/go/pkg/mod/cache \
    && git config --system --add safe.directory /app
CMD ["/bin/bash"]
