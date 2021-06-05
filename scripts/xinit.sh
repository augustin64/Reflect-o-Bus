# We could also have enabled this service via systemd
# But taking it this way allows us to have more control over it
# Enabling our custom service didn't work all the times I've tried
systemctl start reflect-o-bus.service