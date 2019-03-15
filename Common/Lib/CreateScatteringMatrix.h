
//==================================================================================
// SAR Data Analysis Program
//
// File name		: gdal_command.py
// Creation date	: March 18, 2019
// Python version: 3.6
// License   	: GPL v2
// Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
//==================================================================================

#ifndef _CREATESCATTERINGMATRIX_H
#define _CREATESCATTERINGMATRIX_H

#define _CRT_SECURE_NO_WARNINGS 1
#include "stdio.h"
#include "stdlib.h" 
#include "dirent.h"
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
