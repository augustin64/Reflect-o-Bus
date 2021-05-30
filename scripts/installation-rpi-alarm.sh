#!/bin/sh

# Initialize the pacman keyring and populate the Arch Linux ARM package signing keys
pacman-key --init
pacman-key --populate archlinuxarm

# Set the timezone
ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime/
hwclock --systohc

# Generate the locales
echo "fr_FR.UTF-8 UTF-8" > /etc/locale.gen
locale-gen
echo "LANG=fr_FR.UTF-8" > /etc/locale.conf

# keyboard layout
echo "KEYMAP=fr-latin1" > /etc/vconsole.conf

# Hostname
echo "reflect-o-bus" > /etc/hostname

# We are using an install script so we don't want to confirm
pacman -Syu --noconfirm

# We install needed packages
pacman -S netctl dhcpd wpa_supplicant
pacman -S basedevel git
