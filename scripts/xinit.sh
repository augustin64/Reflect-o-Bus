# We could also have enabled this service via systemd
# But taking it this way allows us to have more control over it
# Enabling our custom service didn't work all the times I've tried

# If the system boot is too long because of the git clone, 
# we should maybe delete this line
# /root/reflect-o-bus/scripts/update.sh

# We synchronize time
ntpdate ntp.unicaen.fr
systemctl start reflect-o-bus.service