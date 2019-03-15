
// Copyright (c) 2019 National Institute of Information and Communications Technology
// Released under the GPLv2 license


#define _CRT_SECURE_NO_WARNINGS 1
#include "stdio.h"
#include "stdlib.h" 
#include "dirent.h"
#include "string.h"
#include "CreateScatteringMatrix.h"

using namespace std;

int CreateScatteringMatrix(
	char* infile,
	float* matrix_re,
	float* matrix_im,
	int ncols,
	int nrows,
	int xwin,
	int ywin)
{

	FILE *fr;
	float *temp = NULL;
	int numx = 0; int numy = 0; int count = 0; int numxy = 0;

	int rncols = ncols / xwin;
	int rnrows = nrows / ywin;
	if (rncols * xwin < ncols) rncols++;
	if (rnrows * ywin < nrows) rnrows++;

	fr = fopen(infile, "rb");
	fseek(fr, 32, SEEK_SET);

	size_t readcount = 0;

	while (count < ncols * nrows * 2) {

		temp = (float*)malloc(ncols * 2 * ywin * sizeof(float));
		readcount = fread(temp, sizeof(float), ncols * 2 * ywin, fr);

		for (int jw = 0; jw < ywin; jw++) {
			for (int i = 0; i < rncols; i++) {
				for (int iw = 0; iw < xwin; iw++) {
					if(i + numxy*rncols < rncols * rnrows)
						matrix_re[i + numxy*rncols] = matrix_re[i + numxy*rncols] + temp[2 * i * xwin + 2 * iw + jw * ncols * 2];
						matrix_im[i + numxy*rncols] = matrix_im[i + numxy*rncols] + temp[(2 * i * xwin) + 1 + 2 * iw + jw * ncols * 2];
				}
			}
		}
		count += ncols * 2 * ywin;
		numxy++;
		printf("\r%d/%dloading...", count, ncols*nrows * 2);
		free(temp);
		temp = NULL;

	}
	if (temp != NULL) {
		free(temp);
		temp = NULL;
	}

	for (int num = 0; num < rncols*rnrows; num++) {
		matrix_re[num] = (matrix_re[num] / (xwin*ywin));
		matrix_im[num] = (matrix_im[num] / (xwin*ywin));
	}

	fclose(fr);

	return 0;
}
