#include "SBUS.h"
#include <chrono>
#include <thread>
#include <getopt.h>

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

void send_values(int panValue, int tiltValue, int rollValue, int panChannel, int tiltChannel, int rollChannel) {
	uint16_t channels[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
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
	RONIN.write(&channels[0]);
	std::this_thread::sleep_for(std::chrono::milliseconds(sbusWAIT));


}


void loop() {
	int panValue = 1023;
	int tiltValue = 1023;
	int rollValue = 1023;

	int tiltValues[8] = {424, 1024, 1024, 1624, 1024, 1024, 424, 1024};
	//int tiltValues[8] = {1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024};
	int panValues[8] = {1024, 424, 1024, 1024, 1624, 1024, 1024, 424};
	//int panValues[8] = {1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024};
	//int rollValues[8] = {1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024};
	int rollValues[8] = {1024, 1024, 1624, 1024, 1024, 424, 1024, 1024};
	int val=0;

	std::cout << "Channels:         - T P - R - - - - - - - - - - -" << std::endl;

	for (val=0; val<8; val++) {
		panValue = panValues[val];
		tiltValue = tiltValues[val];
		rollValue = rollValues[val];

		for (int i = 1; i <= 300; i++) {
			send_values(panValue, tiltValue, rollValue, panChannel, tiltChannel, rollChannel);
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(5000));
	}

}

int main(int argc, char* argv[]) {
	setup();
	loop();
}

