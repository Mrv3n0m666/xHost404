# xHost404 - Reverse IP Domain Checker

**xHost404** is a Python script designed for checking domains associated with a list of IP addresses using the Webscan API. The tool makes asynchronous requests to the API, providing a fast and efficient way to retrieve information about domains.

## Features

- Asynchronously checks domains associated with given IP addresses.
- Colorful banners for a visually appealing user experience.
- User-friendly prompts and information text for ease of use.
- Output is saved to `restdomen.txt` with details about the acquired domains.
- Duplicate IP addresses are handled to avoid redundancy.

## How to Use

1. Prepare a file with a list of IP addresses. Each IP address should be on a new line.
    ```plaintext
    example.com
    123.45.678
    example.com
    123.456.78
    ```
2. Run the script:
    ```bash
    python xHost404.py
    ```
3. Enter the path to the file containing IP addresses when prompted.
4. Monitor the progress, and the results will be saved to `restdomen.txt`.
    ![image](https://github.com/Mrv3n0m666/xHost404/assets/157101186/2cab2f44-6864-4cdf-bae7-36d1a527e7d0)


## Getting Started

1. Clone the repository:
    ```bash
    git clone https://github.com/username/xHost404.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the script as described above.

## Contributing

Feel free to contribute to the project by submitting issues or pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to the [Webscan API](https://webscan.cc/) for providing the reverse IP domain lookup service.
- Colorama library for enhancing the script's visual appearance.

