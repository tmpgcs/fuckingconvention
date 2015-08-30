#include <stdio.h>

typedef unsigned long uLong;
typedef unsigned char uChar;
typedef enum 
{
  SNMP_RTS_OK = 0,
  SNMP_RTS_FAILED_GET_SD,
} SNMP_RTS;

typedef struct t_Temp
{
  uLong oasd;
  uChar aa[100];
}tTemp;

SNMP_RTS test_function(void *ar)
{
  tTemp* pasd = ar;
  tTemp lasdsd = *pasd;
  SNMP_RTS ret = SNMP_RTS_OK;
  return ret;
}


int main(int argc, char** argv)
{
  int i = 10;
  uLong ii = i;
  uLong ulfalse;
  uLong ulTrue;
  unsigned int ui_var = 0;
  uChar ccc[10];
  uChar pCCC[10];
  uChar pcCC[10];
  uLong *pi;
  uLong *pTrue;
  uLong *ulAAA;
  uLong *ulaAA;

  test_function(NULL);

  return ii;
}