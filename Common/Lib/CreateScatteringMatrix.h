
// Copyright (c) 2019 National Institute of Information and Communications Technology
// Released under the GPLv2 license

#ifndef _CREATESCATTERINGMATRIX_H
#define _CREATESCATTERINGMATRIX_H

#define _CRT_SECURE_NO_WARNINGS 1
#include "stdio.h"
#include "stdlib.h" 
#include "windows.h"
#include <complex>
#include "string.h"

using namespace std;

__declspec(dllexport) int CreateScatteringMatrix(
	char* infile,
	float* matrix_re,
	float* matrix_im,
	int ncols,
	int nrows,
	int xwin,
	int ywin);

#if !defined(CreateScatteringMatrix)
int CreateScatteringMatrix(
	char* infile,
	float* matrix_re,
	float* matrix_im,
	int ncols,
	int nrows,
	int xwin,
	int ywin
);
#endif

#endif
