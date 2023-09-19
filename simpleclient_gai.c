#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <regex.h>

#define MAX_BUFFER_SIZE 1024
#define SERVER_PORT 8080 // Default server port

void error(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[]) {
    int sockfd;
    struct sockaddr_in server_addr;
    char buffer[MAX_BUFFER_SIZE];
    regex_t regex;
    const char *secret_regex = "^[A-Za-z0-9]+$"; // Modify as needed

    // Compile the regular expression
    if (regcomp(&regex, secret_regex, REG_EXTENDED | REG_NOSUB) != 0) {
        fprintf(stderr, "Failed to compile regular expression\n");
        exit(1);
    }

    // Parse command line arguments
    if (argc < 4 || argc > 5) {
        fprintf(stderr, "Usage: %s [-p port] hostname username\n", argv[0]);
        exit(1);
    }

    int port = SERVER_PORT;
    if (argc == 5 && strcmp(argv[1], "-p") == 0) {
        port = atoi(argv[2]);
    }

    const char *hostname = argv[argc - 2];
    const char *username = argv[argc - 1];

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
        error("ERROR opening socket");

    // Initialize server address structure
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);

    // Resolve hostname to IP address
    struct hostent *server = gethostbyname(hostname);
    if (server == NULL) {
        fprintf(stderr, "ERROR: Could not resolve hostname\n");
        exit(1);
    }
    memcpy(&server_addr.sin_addr.s_addr, server->h_addr, server->h_length);

    // Connect to the server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
        error("ERROR connecting to server");


    // Send initial message
    snprintf(buffer, sizeof(buffer), "cs4254fall2023 HELLO %s\n", username);
    send(sockfd, buffer, strlen(buffer), 0);

    // Receive and process messages
    while (1) {
        memset(buffer, 0, sizeof(buffer));
        int n = recv(sockfd, buffer, sizeof(buffer) - 1, 0);
        if (n <= 0) {
            fprintf(stderr, "Server closed the connection.\n");
            break;
        }

        // Process received message
	//printf("Received: %s", buffer);
        
        char *token = strtok(buffer, " \n");
        if (token == NULL || strcmp(token, "cs4254fall2023") != 0) {
            fprintf(stderr, "Invalid message format: %s\n", buffer);
            continue;
        }

        token = strtok(NULL, " \n"); // Message type
        if (token != NULL && strlen(token) == 64) {
            // Handle BYE message with secret flag
            if(regexec(&regex, token, 0, NULL, 0) == 0)
		printf("%s\n", token);
	    else
		printf("Invalid Secret Key");
	    break;
        } else if (token != NULL && strcmp(token, "STATUS") == 0) {
            // Handle STATUS message
            int operand1, operand2;
            char operator;
            token = strtok(NULL, " \n"); // operand1
            if (token != NULL) operand1 = atoi(token);
            token = strtok(NULL, " \n"); // operator
            if (token != NULL) operator = token[0];
            token = strtok(NULL, " \n"); // operand2
            if (token != NULL) operand2 = atoi(token);

            // Calculate and send solution
            int solution = 0;
            switch (operator) {
                case '+':
                    solution = operand1 + operand2;
                    break;
                case '-':
                    solution = operand1 - operand2;
                    break;
                case '*':
                    solution = operand1 * operand2;
                    break;
                case '/':
                    if (operand2 != 0) {
                        solution = operand1 / operand2;
                    } else {
                        fprintf(stderr, "Division by zero!\n");
                    }
                    break;
                default:
                    fprintf(stderr, "Invalid operator: %c\n", operator);
            }

            snprintf(buffer, sizeof(buffer), "cs4254fall2023 %d\n", solution);
            send(sockfd, buffer, strlen(buffer), 0);
        }
    }

    // Close the socket
    close(sockfd);

    return 0;
}

