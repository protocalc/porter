#include "SBUS.h"
#include <chrono>
#include <thread>
#include <getopt.h>

using namespace std;

SBUS::SBUS RONIN("/dev/ttyAMA0");
int sbusWAIT = 14;

int panChannel = 1;
int tiltChannel = 2;
int rollStab = 4;
int rollChannel = 7;

void setup() {
	RONIN.begin();
	RONIN.setEndPoints(panChannel, 352, 1696);
	RONIN.setEndPoints(tiltChannel, 352, 1696);
	RONIN.setEndPoints(rollChannel, 352, 1696);
}

char* send_values(int panValue, int tiltValue, int rollValue, int panChannel, int tiltChannel, int rollChannel) {
	uint16_t channels[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
	char* gimbal_output;
	for (int chan = 0; chan <= 16; chan++) {
		if (chan == panChannel) {
			channels[panChannel-1] = panValue;	
		}
		else if (chan == tiltChannel) {
			channels[tiltChannel-1] = tiltValue;
		}
		else if (chan == rollChannel) {
			channels[rollChannel-1] = rollValue;
		}
		else if (chan == rollStab) {
			if (rollValue == 1024) {
				channels[rollStab-1] = 1024;
			}
			else {
				channels[rollStab-1] = 0;
			}
		}
	}
	gimbal_output = RONIN.write(&channels[0]);
	std::this_thread::sleep_for(std::chrono::milliseconds(sbusWAIT));

	return gimbal_output;


}


void loop(string datafile) {
	int panValue = 1024;
	int tiltValue = 1024;
	int rollValue = 1024;

	string gimbal_buffer;

	int tiltValues[8] = {1824, 1024, 1524, 1024, 424, 1024, 1324, 724};
	//int tiltValues[8] = {1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024};
	//int panValues[8] = {1024, 424, 1024, 1024, 1624, 1024, 1024, 424};
	int panValues[8] = {1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024};
	int rollValues[8] = {1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024};
	//int rollValues[8] = {424, 1024, 1624, 1024, 1024, 424, 1024, 1024};
	int val=0;

	std::cout << "Channels:         - T P - R - - - - - - - - - - -" << std::endl;

	for (val=0; val<8; val++) {
		panValue = panValues[val];
		tiltValue = tiltValues[val];
		rollValue = rollValues[val];

		char* gimbal_output;

		for (int i = 1; i <= 500; i++) {
			while ((gimbal_output = send_values(panValue, tiltValue, rollValue, panChannel, tiltChannel, rollChannel)) != nullptr) {
				gimbal_buffer.append(gimbal_output);
				free(gimbal_output);
			}
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(5000));
	}

	ofstream out(datafile);
	out << gimbal_buffer;
	out.close();

}

int main(int argc, char* argv[]) {
	string datafile;
	int opt;
	
	static struct option long_options[] = {
		{"output", required_argument, 0, 'o'},
		{0, 0, 0, 0}
	};

	while ((opt = getopt_long(argc, argv, "o:", long_options, nullptr)) != -1) {
		if (opt == 'o') {
			datafile = optarg;
		}
		else {
			cerr << "Usage: " << argv[0] << " --output <filename>\n";
			return 1;
		}
	}
	setup();
	loop(datafile);
}

