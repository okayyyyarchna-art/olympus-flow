FROM --platform={{platform}} public.ecr.aws/d3j8x8q7/olympus-base-python:latest
RUN python -c "import platform; assert platform.python_version() == '{{toolchain_version}}', platform.python_version()"
WORKDIR /app
COPY . .
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.15.3
RUN {{dependency_install}}
RUN {{development_install}}
RUN chmod -R a+rX /app /usr/local/lib/python* \
    && git config --system --add safe.directory /app
CMD ["/bin/bash"]
