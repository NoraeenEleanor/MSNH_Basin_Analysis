"""
Part 1 - Field Inventory + Basin Overview

Part A:
    - wells per quadrant
    - well locations (from Petrel's export)
    
Part B:
    - oil vs. gas, sanctioned vs. unsanctioned
    - field count by reservoir
    - discovery timeline GIF (cum oil vs. gas in year terms)
    
"""

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.style.use('seaborn-v0_8-whitegrid')




#   CONFIG

FIELD_MASTER_FILE       = 'FIELD_MASTER_FINAL.xlsx'
WELL_MASTER_FILE        = 'WELL_MASTER_FINAL.xlsx'
WELLHEAD_FILE           = 'Wellhead'

MAKE_GIFS       = True      # FALSE if want to skip all GIF (faster)
SHOW_PLOTS      = False     # TRUE for pop-up window

WELL_GIF_STEP       = 2
WELL_GIF_FPS        = 8
TIMELINE_GIF_FPS    = 2.5

PALETTE = ['#4C72B0', '#C44E52', '#55A868', '#8172B2', '#CCB974', '#64B5CD']



def finish_fig(filename):
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close()
    print(f'    saved: {filename}')
    
    
    
    
#   LOAD

def well_key(name):
    """Joining the well: disposed space"""
    return re.sub(r'[\s\-]+', '', str(name)).upper()



def load_wells(filepath):
    wells = pd.read_excel(filepath, sheet_name='WELL_MASTER')
    wells = wells.dropna(subset=['FID'])
    wells['WELLREGNO'] = wells['WELLREGNO'].astype(str).str.strip()
    wells['QUAD'] = wells['WELLREGNO'].str.split('/').str[0]
    wells['WELL_KEY'] = wells['WELLREGNO'].map(well_key)
    return wells



def parse_wellhead(filepath):
    """Parse PETREL 'Well heads' ASCII export (custom format, not CSV)"""
    with open(filepath, 'rb') as f:
        raw = f.read()
    text = raw.decode('latin-1')    # NOT utf-8  - for (deg) at Lat/Long
    lines = text.split('\r\n')
    
    idx = lines.index('END HEADER')
    header = ['Name'] + lines[9:idx]
    
    data_lines = [l for l in lines[idx + 1:] if l.strip()]
    rows = [re.findall(r'"[^"]*"|\S+', l) for l in data_lines]
    
    df = pd.DataFrame(rows, columns=header)
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip('"')
    return df



def load_wellhead_xy(filepath):
    raw = parse_wellhead(filepath)
    wellhead = raw[['Name', 'Surface X', 'Surface Y']].copy()
    wellhead.columns = ['WELLREGNO', 'X', 'Y']
    wellhead['X'] = wellhead['X'].astype(float)
    wellhead['Y'] = wellhead['Y'].astype(float)
    wellhead['WELLREGNO'] = wellhead['WELLREGNO'].astype(str).str.strip()
    wellhead['WELL_KEY'] = wellhead['WELLREGNO'].map(well_key)
    return wellhead



def load_fields(filepath):
    sanctioned      = pd.read_excel(filepath, sheet_name='MNSH_FIELD_SANCTIONED')
    unsanctioned    = pd.read_excel(filepath, sheet_name='MNSH_FIELD_UNSANCTIONED')
    
    # Drop blank line/space for both sheets
    sanctioned      = sanctioned.dropna(subset=['FIELDNAME'])
    unsanctioned    = unsanctioned.dropna(subset=['FIELDNAME'])
    
    fields = pd.concat([sanctioned, unsanctioned], ignore_index=True)
    
    # Messy text columns
    fields['FIELDTYPE'] = fields['FIELDTYPE'].astype(str).str.strip().str.upper()
    fields['RESERVOIR'] = fields['RESERVOIR'].astype(str).str.strip()
    fields['SANCTIONED'] = fields['SANCTIONED'].astype(str).str.strip().str.upper()
    return fields




#   PART A: Dataset Overview

def plot_wells_per_quad(wells):
    quad_counts = wells['QUAD'].value_counts().sort_index()
    
    fig, ax = plt.subplots(figsize=(9, 5))
    quad_counts.plot(kind='bar', ax=ax, color=PALETTE[0])
    ax.set_title(f'MNSH Dataset: Wells per Quadrant ({len(wells)} wells, '
                 f'Quads {quad_counts.index.min()}-{quad_counts.index.max()})',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Quadrant'); ax.set_ylabel('Number of Wells')
    finish_fig('part1_intro_wells_per_quad.png')
    
    
    
def merge_well_coord(wells, wellhead):
    wells_geo = wells.merge(wellhead[['WELL_KEY', 'X', 'Y']], on='WELL_KEY', how='left')
    missing = wells_geo.loc[wells_geo['X'].isna(), 'WELLREGNO'].tolist()
    print(f'    len{missing} wells with not found coord after merged'
          + (f': {missing}' if missing else ''))
    return wells_geo



def plot_well_map(wells_geo):
    plotted = wells_geo.dropna(subset=['X', 'Y'])
    
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.scatter(plotted['X'], plotted['Y'], s=20, c=PALETTE[0], alpha=0.7)
    ax.set_title('MNSH Well Locations (UTM Zone 31N, ED50)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Easting (m)'); ax.set_ylabel('Northing (m)')
    ax.set_aspect('equal')
    finish_fig('part1_intro_well_map.png')
    
    
    
def make_well_map_gif(wells_geo):
    wells_sorted = (wells_geo.dropna(subset=['X', 'Y'])
                    .sort_values('QUAD').reset_index(drop=True))
    
    fig, ax = plt.subplots(figsize=(8, 10))
    x_pad = y_pad = 5000
    xlim = (wells_sorted['X'].min() - x_pad, wells_sorted['X'].max() + x_pad)
    ylim = (wells_sorted['Y'].min() - y_pad, wells_sorted['Y'].max() + y_pad)
    
    
    def animate(frame):
        ax.clear()
        current = wells_sorted.iloc[:frame + 1]
        ax.scatter(current['X'], current['Y'], s=20, c=PALETTE[0], alpha=0.7)
        ax.set_xlim(*xlim); ax.set_ylim(*ylim)
        ax.set_aspect('equal')
        ax.set_title(f'MNSH Well Locations - {frame + 1}/{len(wells_sorted)} wells '
                     f'(Quad {current.iloc[-1]["QUAD"]})', fontsize=11, fontweight='bold')
        ax.set_xlabel('Easting (m)'); ax.set_ylabel('Northing (m)')
        
    n_frames = len(wells_sorted)
    frames_idx = list(range(0, n_frames, WELL_GIF_STEP)) + [n_frames - 1]
    
    ani = animation.FuncAnimation(fig, animate, frames=frames_idx, interval=100, repeat=True)
    ani.save('part1_intro_well_map.gif', writer='pillow', fps=WELL_GIF_FPS)
    plt.close()
    print('     saved: part1_intro_well_map.gif')
    
    
    
def run_dataset_overview():
    print('=' * 60)
    print('PART A: DATASET OVERVIEW')
    print('=' * 60)
    
    wells = load_wells(WELL_MASTER_FILE)
    print(f'Loaded {len(wells)} wells across {wells["QUAD"].nunique()} quads')
    
    plot_wells_per_quad(wells)
    
    wellhead = load_wellhead_xy(WELLHEAD_FILE)
    print(f'Parsed {len(wellhead)} wellhead records')
    wells_geo = merge_well_coord(wells, wellhead)
    
    plot_well_map(wells_geo)
    if MAKE_GIFS:
        print('Generating well map GIF...')
        make_well_map_gif(wells_geo)
        
        
        
        
#   PART B: Field Inventory

def print_headline_stats(fields):
    n_with_year = fields['YEARDISC'].notna().sum()
    n_distinct = fields['FIELDNAME'].astype(str).str.strip().str.upper().nunique()
    print(f'\nFeild-reservoir record: {len(fields)} | different fields: {n_distinct}')
    dup = fields[fields['FIELDNAME'].astype(str).str.strip().str.upper().duplicated(keep=False)]
    if len(dup):
        print('Field appeares more than once (diff reservoirs):')
        print(dup[['FIELDNAME', 'RESERVOIR', 'SANCTIONED']].to_string(index=False))
    print(f'FIELDTYPE: {fields["FIELDTYPE"].value_counts().to_dict()}')
    print(f'SANCTIONED: {fields["SANCTIONED"].value_counts().to_dict()}')
    if n_with_year:
        print(f'Discovery years: {int(fields["YEARDISC"].min())} - {int(fields["YEARDISC"].max())}')
    print(f'Fields without YEARDISC: {len(fields) - n_with_year} '
          f'(data gap - not include in the timeline)')
    
    
    
def plot_type_by_sanctioned(fields):
    crosstab = pd.crosstab(fields['FIELDTYPE'], fields['SANCTIONED'])
    print('\nField Type x Sanctioned Status')
    print(crosstab.to_string())
    
    fig, ax = plt.subplots(figsize=(7, 5))
    crosstab.plot(kind='bar', ax=ax, color=PALETTE[:crosstab.shape[1]])
    ax.set_title('MNSH Field Type by Sanctioned Status', fontsize=13, fontweight='bold')
    ax.set_xlabel('Field Type'); ax.set_ylabel('Number of Fields')
    ax.legend(title='Sanctioned')
    plt.xticks(rotation=0)
    finish_fig('part1_fieldtype_sanctioned.png')
    
    
    
def plot_reservoir_counts(fields):
    reservoir_counts = fields['RESERVOIR'].value_counts()
    print('\nField count by reservoir:')
    print(reservoir_counts.to_string())
    
    fig, ax = plt.subplots(figsize=(8, 6))
    reservoir_counts.sort_values().plot(kind='barh', ax=ax, color=PALETTE[2])
    ax.set_title('Field Count by Reservoir', fontsize=13, fontweight='bold')
    ax.set_xlabel('Number of Fields')
    finish_fig('part1_reservoir_counts.png')
    
    
    
def make_discovery_timeline_gif(fields):
    timeline = fields.dropna(subset=['YEARDISC']).copy()
    timeline['YEARDISC'] = timeline['YEARDISC'].astype(int)
    
    types = sorted(timeline['FIELDTYPE'].unique())
    type_colors = {t: PALETTE[i % len(PALETTE)] for i, t in enumerate(types)}
    
    year_range = list(range(timeline['YEARDISC'].min(), timeline['YEARDISC'].max() + 1))
    y_max = timeline['FIELDTYPE'].value_counts().max() + 2
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    def animate(frame):
        ax.clear()
        current_year = year_range[frame]
        cum = timeline[timeline['YEARDISC'] <= current_year]
        
        counts = cum['FIELDTYPE'].value_counts().reindex(types, fill_value=0)
        
        ax.bar(types, counts.values, color=[type_colors[t] for t in types])
        ax.set_ylim(0, y_max)
        ax.set_title(f'MNSH Field Discoveries - up to {current_year}', fontsize=13, fontweight='bold')
        ax.set_ylabel('Cumulative Fields Discovered')
        
    ani = animation.FuncAnimation(fig, animate, frames=len(year_range), interval=400, repeat=True)
    ani.save('part1_discovery_timeline.gif', writer='pillow', fps=TIMELINE_GIF_FPS)
    plt.close()
    print(' saved: part1_discovery_timeline.gif')
    
    
    
def run_field_inventory():
    print('\n' + '=' * 60)
    print('PART B: FIELD INVENTORY')
    print('=' * 60)
    
    fields = load_fields(FIELD_MASTER_FILE)
    print_headline_stats(fields)
    
    print('\nGenerating field charts...')
    plot_type_by_sanctioned(fields)
    plot_reservoir_counts(fields)
    
    if MAKE_GIFS:
        print('Generating discovery timeline GIF...')
        make_discovery_timeline_gif
        
        
        
        
#   MAIN

def main():
    run_dataset_overview()
    run_field_inventory()
    print('\nDone!')
    
    
    
if __name__ == '__main__':
    main()