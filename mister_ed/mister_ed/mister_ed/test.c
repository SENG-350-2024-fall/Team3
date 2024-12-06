#include < stdio.h>     /* Routines for input/output. */
#include "threads.h"    /* Routines for thread creation/synchronization. */

#define N 100           /* Number of elements in each vector. */
#define P 4             /* Number of processors for parallel execution. */

double a[N], b[N];      /* Vectors for computing the dot product. */
double partial_sums[P]; /* Array of results computed by threads. */
volatile int thread_id_counter
double dot_product = 0.0;
Barrier bar;            /* Shared variable to support barrier synchronization. */

void ParallelFunction(void)
{
    int my_id, i, start, end;
    double s;
    my_id = get_my_thread_id();      /* Get unique identifier for this thread. */
    start = (N / P) * my_id;         /* Determine start/end using thread identifier. */
    end = (N / P) * (my_id + 1) – 1; /* N is assumed to be evenly divisible by P .* /
    s = 0.0;
    for (i = start; i <= end; i++)
        s = s + a[i] * b[i];
    partial_sums[my_id] = s;         /* Save result in array. */
    barrier(&bar, P);                /* Synchronize with other threads. */

    while (thread_id_counter != my_id) {
        dot_product += partial_sums[my_id];
        thread_id_counter = (thread_id_counter + 1) % P;
        break;
    }
}
void main(void)
{
    int i;

    <Initialize vectors a[], b[] – details omitted.> 
    init_barrier(&bar);

    for (i = 1; i < P; i++) /* Create P – 1 additional threads. */
        create_thread(ParallelFunction);

    ParallelFunction(); /* Main thread also joins parallel execution. */

    printf("The dot product is %g\ n", dot_product);
}