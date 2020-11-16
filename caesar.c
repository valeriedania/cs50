//include libraries
#include <cs50.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>

//Implement single command-line argument
int main(int argc, string argv[])


{
    //Declare variables
    int argv_length, key, plaintext_length;
    string ciphertext;
    
      //Check single command-line argument
      if (argc != 2)
      {
        printf("Usage: ./caesar key\n");
        return 1;
      }
      
     
      //Verify that argv is an int or else convert
      argv_length = strlen(argv[1]);
      key = atoi(argv[1]);
      for (int i = 0; i < argv_length; i++)
      {
        if (argv[1][i] < 48 || argv[1][i] > 57)
      {
        printf("Usage: ./caesar key\n");
        return 1;
      }
      else 
      {
        key = atoi(argv[1]);
      }

    }
  
 
    //Prompt user for plaintext
      
    string plaintext = get_string("plaintext:");
    plaintext_length = strlen(plaintext);
    
    //Use a loop to iterate over every char in text
    for (int i = 0; i < plaintext_length; i++)
    {
      //Check if char is lowercase or uppercase and a letter
      if (isalpha(plaintext[i]))
      {
        
        if (isupper(plaintext[i]))
        {
        printf("ciphertext: %c", (((plaintext[i] - 65) + key) % 26) + 65);
        
        }
        else  
        {
        printf("ciphertext: %c", (((plaintext[i] - 97) + key) % 26) + 97);
        }
      
      }
       else 
       {
        printf("ciphertext: %c", (plaintext[i]));
       }
      
    }
    printf("\n");
    return 0;
}