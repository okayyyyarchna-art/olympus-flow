FROM public.ecr.aws/d3j8x8q7/olympus-base:latest
RUN node -e "if(process.versions.node !== '{{toolchain_version}}')process.exit(1)"
RUN {{package_manager_install}}
WORKDIR /app
COPY . .
RUN {{fetch_command}} \
    && cp -a node_modules /opt/adapter-node_modules
RUN {{development_install}}
RUN chmod -R a+rX /opt/adapter-node_modules \
    && chmod -R a+rwX /app \
    && git config --system --add safe.directory /app
CMD ["/bin/bash"]
