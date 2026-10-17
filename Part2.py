"""
Part 1 - Well Database QC + Formation Tops Analysis

Part A: Well Database QC
    - normalize flag columns (Y / y / 'Y ' / P / NaN )
    - completeness score for each well
    - traffic-light matrix (wells x flags)
    - average completeness by quadrant
    - (optional) GIF: matrix reveal by quad
    
Part B: Formation Tops Analysis
    - wells penetrate for each formation (by stratigraphy)
    - formation penertation count by quadrant (heatmap)
    - top 10 most targeted formations
    
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.style.use('seaborn-v0_8-whitegrid')




#   CONFIG

WELL_MASTER_FILE    = 'WELL_MASTER_FINAL.xlsx'
WELL_TOPS_FILE      = 'WELL_TOPS_FINAL.xlsx'

MAKE_GIF        = True      # FALSE if want to skip all GIF (faster)
SHOW_PLOTS      = False     # TRUE for pop-up window
GIF_STEP        = 3         # smaller = smoother (but longer time)
GIF_FPS         = 8

FLAG_COLS = ['DOWNLOADED', 'DHA', 'COMP_LOG', 'PENETRATIONS', 'TOPS_FT', 'TOPS_M',
             'TOPS_PETREL', 'CHECKSHOT', 'S2W_TIE', 'CORE', 'WELL_SUMMARY', 'FINISHED']


# Formation by stratigraphy (shallower to deepest level)
FORMATION_ORDER = [
    'PLIOCENE', 'MIOCENE', 'OLIGOCENE', 'EOCENE', 'PALAEOCENE',
    'U_CRET', 'L_CRET', 'U_JURASSIC', 'L_JURASSIC', 'U_TRIASSIC',
    'L_TRIASSIC', 'ZECHSTEIN', 'PLATTENDOLOMIT', 'ROTLIEGEND',
    'CARBONIFEROUS', 'WESTPHALIAN', 'MILLSTONE_GRIT', 'YOREDALE',
    'SCREMERSTON', 'FELL_SST', 'CEMENTSTONE', 'DEVONIAN',
    'OLD_RED_SST', 'KYLE_LST', 'SILURIAN', 'BASEMENT',
]



def finish_fig(filename):
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close()
    print(f'    saved: {filename}')
    
    
    
    
#   LOAD

def load_wells(filepath):
    wells = pd.read_excel(filepath, sheet_name='WELL_MASTER')
    wells = wells.dropna(subset=['FID'])
    wells['QUAD'] = wells['WELLREGNO'].astype(str).str.strip().str.split('/').str[0]
    return wells




#   PART A: WELL DATABASE QC

def normalize_flag(series):
    return series.astype(str).str.strip().str.upper().replace({'NAN': np.nan, 'NONE':np.nan})



def inspect_flags(wells, label):
    print(f'\n{label}')
    for col in FLAG_COLS:
        print(f'    {col} -> {sorted(map(str, wells[col].unique()))}')
        
        
        
def add_completeness(wells):
    wells['COMPLETENESS_SCORE'] = wells[FLAG_COLS].apply(lambda row: (row == 'Y').sum(), axis=1)
    wells['COMPLETENESS_PCT']   = wells['COMPLETENESS_SCORE'] / len(FLAG_COLS) * 100
    return wells



def flag_matrix_numeric(wells):
    matrix = wells.set_index('WELLREGNO')[FLAG_COLS]
    return matrix.apply(lambda col: col.map({'Y': 2, 'P': 1}).fillna(0))



def plot_traffic_light(wells):
    matrix_numeric = flag_matrix_numeric(wells)
    
    fig, ax = plt.subplots(figsize=(8, 14))
    ax.imshow(matrix_numeric.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=2)
    ax.set_xticks(range(len(FLAG_COLS)))
    ax.set_xticklabels(FLAG_COLS, rotation=45, ha='right')
    ax.set_yticks(range(len(matrix_numeric)))
    ax.set_yticklabels(matrix_numeric.index, fontsize=6)
    ax.set_title('Well Data Availability - Traffic Light Matrix', fontsize=13, fontweight='bold')
    finish_fig('part2_traffic_light_matrix.png')
    
    
    
def plot_completeness_by_quad(wells):
    completeness_by_quad = wells.groupby('QUAD')['COMPLETENESS_PCT'].mean().sort_values()
    
    fig, ax = plt.subplots(figsize=(9, 6))
    completeness_by_quad.plot(kind='barh', ax=ax, color='#55A868')
    ax.set_title('Average Data Completeness by Quadrant', fontsize=13, fontweight='bold')
    ax.set_xlabel('Completeness (%)')
    finish_fig('part2_completeness_by_quad.png')
    
    
    
def make_traffic_light_gif(wells):
    wells_sorted = wells.sort_values('QUAD').reset_index(drop=True)
    matrix_numeric = flag_matrix_numeric(wells_sorted)
    
    fig, ax = plt.subplots(figsize=(8, 14))
    
    def animate(frame):
        ax.clear()
        current = matrix_numeric.iloc[:frame + 1]
        ax.imshow(current.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=2)
        ax.set_xticks(range(len(FLAG_COLS)))
        ax.set_xticklabels(FLAG_COLS, rotation=45, ha='right', fontsize=8)
        ax.set_yticks([])
        current_quad = wells_sorted.iloc[frame]['QUAD']
        ax.set_title(f'Well Data Availability - {frame + 1}/{len(matrix_numeric)} wells {current_quad}',
                     fontsize=11, fontweight='bold')
        
    n_frames = len(matrix_numeric)
    frames_idx = list(range(0, n_frames, GIF_STEP)) + [n_frames - 1]
        
    ani = animation.FuncAnimation(fig, animate, frames=frames_idx, interval=100, repeat=True)
    ani.save('part2_traffic_light_matrix.gif', writer='pillow', fps=GIF_FPS)
    plt.close()
    print(' saved: part2_traffic_light_matrix.gif')
        
        
        
def run_well_qc(wells):
    print('=' * 60)
    print('PART A: WELL DATABASE QC')
    print('=' * 60)
    
    inspect_flags(wells, 'Flag values BEFORE normalize:')
    for col in FLAG_COLS:
        wells[col] = normalize_flag(wells[col])
    inspect_flags(wells, 'Flag values AFTER normalize:')
        
    wells = add_completeness(wells)
    print('\nTop 10 most completed wells:')
    print(wells[['WELLREGNO', 'QUAD', 'COMPLETENESS_SCORE', 'COMPLETENESS_PCT']]
          .sort_values('COMPLETENESS_PCT', ascending=False).head(10).to_string(index=False))
    
    print('\nGenerating QC charts...')
    plot_traffic_light(wells)
    plot_completeness_by_quad(wells)
    
    if MAKE_GIF:
        print('Generating traffic-light GIF...')
        make_traffic_light_gif(wells)
        
    
    return wells




#   PART B: FORMATION TOPS ANALYSIS

def load_penetrations(filepath, wells):
    pen = pd.read_excel(filepath, sheet_name='PENETRATIONS')
    pen = pen.dropna(subset=['FID'])
    pen = pen.merge(wells[['FID', 'QUAD']], on='FID', how='left')
    for col in FORMATION_ORDER:
        pen[col] = pen[col].astype(str).str.strip().str.upper()
    return pen



def plot_penetrations_by_formation(penetration_counts):
    fig, ax = plt.subplots(figsize=(10, 7))
    penetration_counts.plot(kind='barh', ax=ax, color='#4C72B0')
    ax.invert_yaxis()       # shallower ta top , deepest at bottom
    ax.set_title('Well Peenetrations by Formation (Shallow -> Deep)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Number of Wells Penetrating')
    finish_fig('part2_penetrations_by_formation.png')
    
    
    
def plot_formation_by_quad(pen):
    quad_formation = pen.groupby('QUAD')[FORMATION_ORDER].apply(lambda df: (df == 'Y').sum())
    
    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(quad_formation.values, cmap='YlGnBu', aspect='auto')
    ax.set_xticks(range(len(FORMATION_ORDER)))
    ax.set_xticklabels(FORMATION_ORDER, rotation=90, fontsize=8)
    ax.set_yticks(range(len(quad_formation)))
    ax.set_yticklabels(quad_formation.index)
    ax.set_title('Formation Penetration Count by Quadrant', fontsize=13, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Well Count')
    finish_fig('part2_formation_by_quad_heatmap.png')
    
    
    
def plot_top_formations(pen, penetration_counts):
    total_wells = pen['FID'].nunique()
    top_formations = (penetration_counts / total_wells * 100).sort_values(ascending=False).head(10)
    
    print('\nTop 10 most targeted formations (% of wells):')
    print(top_formations.round(1).to_string())
    
    fig, ax = plt.subplots(figsize=(9, 6))
    top_formations.plot(kind='bar', ax=ax, color='#C44E52')
    ax.set_title('Top 10 Most-Targeted Formations (% of Wells)', fontsize=13, fontweight='bold')
    ax.set_ylabel('% of Wells Penetrating')
    plt.xticks(rotation=45, ha='right')
    finish_fig('part2_top_formations.png')
    
    
    
def run_formation_tops(wells):
    print('\n' + '=' * 60)
    print('PART B: FORMATION TOPS ANALYSIS')
    print('=' * 60)
    
    pen = load_penetrations(WELL_TOPS_FILE, wells)
    print(f'Penetrations table: {pen.shape[0]} wells x {len(FORMATION_ORDER)} formations')
    
    penetration_counts = pd.Series({f: (pen[f] == 'Y').sum() for f in FORMATION_ORDER})
    print('\nWells penetrating each formation:')
    print(penetration_counts.to_string())
    
    print('\nGenerating formation charts...')
    plot_penetrations_by_formation(penetration_counts)
    plot_formation_by_quad(pen)
    plot_top_formations(pen, penetration_counts)
    
    
    
    
#   MAIN

def main():
    wells = load_wells(WELL_MASTER_FILE)
    print(f'Loaded {len(wells)} wells across {wells["QUAD"].nunique()} quads')
    
    wells = run_well_qc(wells)
    run_formation_tops(wells)
    
    print('\nDone!')
    
    
if __name__ == '__main__':
    main()