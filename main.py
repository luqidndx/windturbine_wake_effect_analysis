# -*- coding: utf-8 -*-
"""
@author: luqi
@Created on
@instruction：
@Version update log:
"""

import intervals as I
import pandas as pd
import numpy as np
import math
import datetime
import timeit
import os

from function import tur_site_display
from function import distance
from function import angular_deflection
from function import making_directionary

start = timeit.default_timer()

report_version_time = datetime.datetime.now().strftime('%Y%m%d-%H%M')
output_path = 'output/{}'.format(report_version_time)
making_directionary.making_dir(output_path)
site_info = pd.read_csv('input_windfarm_info/site_info.csv', header=0)

windfarm_fig = tur_site_display.turbinesite(site_info['X(m)'], site_info['Y(m)'], site_info['LABEL'],
                                            site_info['rotor diameter(m)'], output_path)

writer = pd.ExcelWriter(os.path.join(output_path, 'result_{}.xlsx'.format(report_version_time)))
for i in range(len(site_info['LABEL'])):  # 第一层主循环，循环所有风机的测试扇区
    result = site_info[['LABEL', 'X(m)', 'Y(m)']]
    influence_sectors = I.empty()
    for j in range(len(site_info['LABEL'])):  # 第二层循环，计算i号风机与所有其他风机相关位置关系、受影响扇区，并确定i号风机测试扇区
        if j == i:  # 跳过自身
            continue
        ln = distance.distance(site_info['X(m)'][i], site_info['Y(m)'][i],
                               site_info['X(m)'][j], site_info['Y(m)'][j])
        ld = ln / site_info['rotor diameter(m)'][i]
        if ld > 20:
            influence_degree = 0
        else:
            influence_degree = 1.3 * (math.atan(2.5 * ld ** (-1) + 0.15) / math.pi * 180) + 10
        tem_azimuth = math.degrees(np.arctan2(site_info['Y(m)'][j] - site_info['Y(m)'][i],  # Y轴坐标差
                                              site_info['X(m)'][j] - site_info['X(m)'][i]))  # X轴坐标差
        # numpy.arctan2(y-cor, x-cor)，对应的坐标系为x正方向为0，逆时针到180°，顺时针到-180°,角度为i指向j的向量
        azimuth = angular_deflection.angular_deflection(tem_azimuth)
        influence_sector = I.open(round(azimuth - influence_degree / 2, 2), round(azimuth + influence_degree / 2, 2))
        result.loc[j, 'Ln'] = round(ln, 2)
        result.loc[j, 'Ln/Dn'] = round(ld, 2)
        result.loc[j, 'influence_degree'] = round(influence_degree, 2)
        result.loc[j, 'azimuth'] = round(azimuth, 2)
        result.loc[j, 'influence_sector'] = influence_sector
        influence_sectors = influence_sectors.union(influence_sector)  # 机位影响扇区
    testing_sectors = I.closed(0, 360) - influence_sectors  # 测试扇区
    # result.set_value(i, 'influence_sectors', influence_sectors)
    # result.set_value(i, 'testing_sectors', testing_sectors)
    result.loc[i, 'influence_sectors'] = str(influence_sectors)
    result.loc[i, 'testing_sectors'] = str(testing_sectors)

    result.to_excel(writer, sheet_name='WTG{}'.format(site_info['LABEL'][i]), startrow=0, startcol=0, index=False)
writer.close()

end = timeit.default_timer()
print('Running time: %s Seconds' % (end - start))
print('Finished')
