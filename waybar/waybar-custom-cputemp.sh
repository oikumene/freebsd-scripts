#! /bin/sh

# ~/.config/waybar/config should be like:
# {
#     "custom/cputemp": {
#         "exec": "~/bin/waybar-custom-cputemp.sh",
#         "interval": 10
#     }
# }

# ~/.config/waybar/style.css should be like this:
# #custom-cputemp {
#     background-color: #d88456;
#     color: #000000;
#     padding: 0 10px;
# }

temp_max=0
cpu_max=0
tooltip=""
ncpu=$(sysctl hw.ncpu | sed "s/^.*: //")

for n in $(jot ${ncpu} 0); do
	temp=$(sysctl "dev.cpu.${n}.temperature" | sed "s/^.*: //" | tr -d C)
	tooltip="${tooltip}CPU ${n}: ${temp}°C"
	if [ $(bc -e "${temp} > ${temp_max}") -eq 1 ]; then
		temp_max=${temp}
		cpu_max=${n}
	fi
done

text="CPU ${cpu_max}: ${temp_max}°C"
tooltip=${tooltip%?}
class="custom-cputemp"

echo "${text}"
echo "${tooltip}"
echo "${class}"
