// Experiment with the stack.  Written by Matt Godbolt.
// Use it however you like.
#include <stdio.h>
#include <string.h>
#include <stdlib.h>


// Filthy nasty routine to poke below the stack pointer.
// Never do this in production code, it's almost certain
// to go wrong.
void PokeStack(int offset)
{
#ifdef WIN32
  char *stack_pointer;
  __asm mov stack_pointer, esp;
#else
  register char *stack_pointer __asm__ ("esp");
#endif
  stack_pointer[-offset] = 0;
}

// The code I eventually developed to defeat MS's compiler's optimiser.
// Without this (e.g. just using "memset" to fill the stack array), the
// compiler is clever enough to notice that ProbeStack() is essentially
// a no-op, and removes it.
void DefeatOptimiser(volatile char* input, volatile char* input2, int size)
{
  for (int i = 0; i < size; ++i)
    *input++ = static_cast<char>((i & 0xff) + (input2 ? input2[i] : 0));
}

// Recursively probe the stack in chunks of log_chunk_size.  The second
// parameter points at the caller's stack variable to prevent the
// MS compiler again from folding all the stack variables into one.
template<int log_chunk_size>
void ProbeStack(int kilobytes, volatile char* defeat_stack_folding = 0)
{
  if (kilobytes <= 0)
    return;
  const int chunk_size = (1<<log_chunk_size);
  volatile char stack_eater[chunk_size * 1024];
  DefeatOptimiser(stack_eater, defeat_stack_folding, chunk_size * 1024);
  kilobytes -= chunk_size;
  ProbeStack<log_chunk_size>(kilobytes, stack_eater);
}

// Win32 specific filter, used in catching the stack overflow exceptions.
// Mainly to prevent the annoying "This program has performed an illegal
// operation" box up while we forcibly crash the program.
#ifdef WIN32
static int filter() { return 1; }
#endif

int main(int argc, const char* argv[])
{
#ifdef WIN32
  __try {
#endif
  if (argc==1) {
    printf("-----\nProbing stack with local variables\n");
    for (int log_chunk_size = 1; log_chunk_size <= 11; ++log_chunk_size) {
      bool failed = false;
      int chunk_size = 1 << log_chunk_size;
      for (int stack_probe = chunk_size; stack_probe <= 4*1024; stack_probe += chunk_size) {
        char buf[1024];
        sprintf(buf, "\"%s\" %d %d", argv[0], log_chunk_size, stack_probe);
        if (system(buf))
        {
          printf("Failed at stack size %dK chunk size %dK\n", stack_probe, chunk_size);
          failed = true;
          break;
        }
      }
      if (!failed) {
        printf("Succeeded at chunk size %dK\n", chunk_size);
      }
    }
    printf("-----\nPoking back directly\n");
    for (int poke_back = 1; poke_back < 512; poke_back *= 2) {
      char buf[1024];
      sprintf(buf, "\"%s\" %d", argv[0], poke_back);
      if (system(buf))
      {
        printf("Failed at poke back size %dK\n", poke_back);
        break;
      }
    }
    printf("Done\n");
  } else if (argc==2) {
    int poke_back = atoi(argv[1]);
    //printf("Trying to probe back manually %dK\n", poke_back);
    PokeStack(poke_back * 1024);
  } else if (argc==3) {
    int log_chunk_size = atoi(argv[1]);
    int stack_size = atoi(argv[2]);
    //printf("Trying stack of %dK using %dK chunks...\n", stack_size, 1<<log_chunk_size);
    switch (log_chunk_size) {
      case 1: ProbeStack<1>(stack_size); break;
      case 2: ProbeStack<2>(stack_size); break;
      case 3: ProbeStack<3>(stack_size); break;
      case 4: ProbeStack<4>(stack_size); break;
      case 5: ProbeStack<5>(stack_size); break;
      case 6: ProbeStack<6>(stack_size); break;
      case 7: ProbeStack<7>(stack_size); break;
      case 8: ProbeStack<8>(stack_size); break;
      case 9: ProbeStack<9>(stack_size); break;
      case 10: ProbeStack<10>(stack_size); break;
      case 11: ProbeStack<11>(stack_size); break;
    }
  }
  return 0;
#ifdef WIN32
  } __except (filter()) { return 1; }
#endif
}
