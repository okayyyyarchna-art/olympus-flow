FROM --platform={{platform}} public.ecr.aws/d3j8x8q7/olympus-base-python:latest
RUN python -c "import platform; assert platform.python_version() == '{{toolchain_version}}', platform.python_version()"
WORKDIR /app
COPY . .
{{build_environment}}
RUN {{dependency_install}}
RUN {{development_install}}
RUN find /app /usr/local/lib/python* -type d ! -perm -005 -exec chmod a+rx {} + \
    && find /app /usr/local/lib/python* -type f ! -perm -004 -exec chmod a+r {} + \
    && git config --system --add safe.directory /app
CMD ["/bin/bash"]
