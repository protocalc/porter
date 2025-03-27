#include "SBUS.h"
#include <chrono>
#include <thread>

SBUS::SBUS RONIN("/dev/ttyAMA0");


int sbusWAIT = 500;

int panChannel = 2;
int tiltChannel = 1;
int rollChannel = 4;

void setup() {
	RONIN.begin();
	RONIN.setEndPoints(panChannel, 352, 1696);
	RONIN.setEndPoints(tiltChannel, 352, 1696);
	RONIN.setEndPoints(rollChannel, 352, 1696);
}

void send_values(int panValue, int rollValue, int tiltValue, int panChannel, int tiltChannel, int rollChannel) {
	uint16_t channels[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
	for (int chan = 0; chan <= 16; chan++) {
		if (chan == panChannel) {
			channels[panChannel] = panValue;	
		}
		else if (chan == tiltChannel) {
			channels[tiltChannel] = tiltValue;
		}
		else if (chan == rollChannel) {
			channels[rollChannel] = rollValue;
		}
	}
	RONIN.write(&channels[0]);
	std::this_thread::sleep_for(std::chrono::milliseconds(sbusWAIT));


}


void loop() {
	int panValue = 1023;
	int tiltValue = 1023;
	int rollValue = 1023;

	int tiltValues[8] = {1324, 1024, 724, 1024, 1324, 1024, 724, 1024};
	int panValues[8] = {1024, 1324, 1024, 724, 1024, 1324, 1024, 724};
	int rollValues[8] = {1024, 724, 1024, 1324, 1024, 724, 1024, 1324};
	int val=0;

	for (val=0; val<8; val++) {
		panValue = panValues[val];
		tiltValue = tiltValues[val];
		rollValue = rollValues[val];

		for (int i = 1; i <= 10; i++) {
			send_values(panValue, rollValue, tiltValue, panChannel, tiltChannel, rollChannel);
		}
	}
}

int main() {
	setup();
	loop();
}

