"""연결된 RealSense 카메라가 있는지 확인한다."""

import sys

from realsense_capture.camera import list_devices


def main() -> None:
    devices = list_devices()

    if not devices:
        print("연결된 RealSense 카메라가 없습니다.")
        sys.exit(1)

    print(f"연결된 RealSense 카메라 {len(devices)}대:")
    for device in devices:
        print(
            f"  - {device['name']} "
            f"(serial: {device['serial_number']}, "
            f"firmware: {device['firmware_version']})"
        )


if __name__ == "__main__":
    main()
