# Digitization Guide: Adding Experimental Data to cfd-vv-suite

This guide explains how to extract reference data from published experimental graphs and add it to the project.

## When to digitize

Many experimental papers present results as graphs rather than tables. To use these as validation data:

1. The paper must be from a reputable source (journal, conference, technical report)
2. The experimental setup should be well-documented (geometry, flow conditions, measurement technique)
3. The graphs should be clear and high-resolution
4. Measurement uncertainties should be quoted

## Tools

Recommended free tool: **WebPlotDigitizer** (https://automeris.io)

```bash
# Install (web version works without installation)
# Or use the desktop app:
# https://github.com/ankitrohatgi/WebPlotDigitizer/releases
```

Alternative: **PlotDigitizer** (https://plotdigitizer.com), **Engauge Digitizer**

### Wolfram Mathematica

If you have access to Wolfram Mathematica, the built-in image processing tools provide a fast digitization workflow (2-3 minutes per graph):

1. Import the graph image:
   ```mathematica
   img = Import["figure.png"];
   ```

2. Use `LocatorPane` for interactive calibration — click known axis points:
   ```mathematica
   pts = {{x1, y1}, {x2, y2}};  (* replace with axis min/max coordinates *)
   ```

3. Extract the curve with `ImageLines` or manual tracing via `Graphics` + `Locator`:
   ```mathematica
   curve = ImageData[Binarize[img, 0.5]];
   (* or use DynamicModule with Locator for interactive point selection *)
   ```

4. Transform pixel coordinates to physical units with `LinearModelFit` or a manual affine transform:
   ```mathematica
   transform[{px_, py_}] := {
       a1 + b1*px + c1*py,
       a2 + b2*px + c2*py
   };
   (* fit coefficients from calibration points *)
   ```

5. Export to CSV for cfd-vv-suite:
   ```mathematica
   Export["reference/experimental/profile.csv", data, "CSV"]
   ```

Tips for Mathematica digitization:
- Use `ImageTake` to crop to the graph area before processing
- `ColorNegate` and `Binarize` help isolate curves from the background
- `FindPeaks` can automate extraction from profile plots
- `ComponentMeasurements` is useful for scatter plot digitization

## Step-by-step workflow

### 1. Obtain a high-resolution image

- Download the PDF of the paper
- Use a screenshot tool at high zoom (Windows: Win+Shift+S at 200%+ zoom)
- Crop to the graph area only
- Save as PNG (lossless)

### 2. Calibrate axes

In WebPlotDigitizer:

1. File -> Load Image
2. Click on "2D (X-Y) Plot"
3. Align axes: click "Axes" -> "Calibrate Axes"
4. Set four calibration points:
   - X-min, Y-min (bottom-left of axes)
   - X-max, Y-min (bottom-right)
   - X-min, Y-max (top-left)
   - X-max, Y-max (top-right)
5. Enter the actual numerical values for each calibration point
6. Verify: check several tick marks to ensure the calibration is correct

### 3. Extract data points

- Use "Automatic Extraction" for curves (color-based detection)
- Use "Manual Mode" for sparse data or noisy backgrounds
- For profile plots (e.g., u(y) profile): use "Automatic" with a line width of 3-5 pixels
- For scatter plots: use "Manual Mode" and click on each visible data point
- Export as CSV: File -> Export Data -> CSV

### 4. Format for cfd-vv-suite

The exported CSV needs to be transformed to the project format:

```python
import csv

# Example: digitized velocity profile u(y/c) at x/c=0.5
# WebPlotDigitizer output: x_pixel, y_pixel, u_Uinf
# We need: y, u, v  (or x, y, u, v for 2D)

with open('digitized.csv', 'r') as f_in:
    reader = csv.reader(f_in)
    next(reader)  # skip header
    data = [(float(row[1]), float(row[2])) for row in reader]

with open('reference/experimental/profile_mid.csv', 'w', newline='') as f_out:
    w = csv.writer(f_out)
    w.writerow(['y', 'u', 'v'])  # standard field names
    for y, u in data:
        w.writerow([y, u, 0.0])
```

### 5. Document the source

Every digitized dataset requires:

1. **Source paper**: full citation with DOI/URL in `case.yaml` and `README.md`
2. **Original figure number**: e.g., "Digitized from Fig. 7"
3. **Measurement method**: e.g., "LDA velocity measurements", "Pressure taps"
4. **Uncertainty**: quoted from the paper or estimated from digitization accuracy
5. **Digitization date and tool**: e.g., "Digitized with WebPlotDigitizer v4.6, 2026-07"

Add this information to the `README.md` of the case and to `docs/data-provenance.md`.

### 6. Add to case.yaml

```yaml
reference:
  type: experimental
  source: "Author et al. Journal, Vol, pp, Year. Digitized from Fig. X."
  doi: "https://doi.org/..."  # if available
  digitization:
    tool: "WebPlotDigitizer v4.6"
    figure: "Fig. 7"
    notes: "21 points extracted from u/U_inf vs y/delta plot"
```

### 7. Verify digitization accuracy

```bash
# Compare digitized data against known checkpoints
# For example, the maximum value should match the quoted value in the paper
python -c "
import numpy as np
data = np.loadtxt('reference/experimental/profile.csv', delimiter=',', skiprows=1)
print(f'Max u/U_inf = {np.max(data[:,1]):.4f} (paper quotes: 0.995)')
print(f'{len(data)} points extracted')
"
```

### 8. Add data provenance entry

Update `docs/data-provenance.md` with a new entry describing what was digitized and how.

## Quality checklist

Before submitting a digitized dataset:

- [ ] Axes are correctly calibrated (compare tick marks)
- [ ] The curve is correctly traced (compare visually)
- [ ] Quantities match known integral values from the paper (e.g., Cd, Nu)
- [ ] Number of points is sufficient (typically 50-200 for a smooth profile)
- [ ] Data is in the correct physical units (check axis labels)
- [ ] Field names follow the project convention (u, v, w, p, T, Cp, Cf, ...)
- [ ] Source is properly cited with DOI/URL
