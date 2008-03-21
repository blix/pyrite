#!/usr/bin/env python
#
# Pyrite taking the best from git an hg
#
#Copyright 2008 Govind Salinas <blix@sophiasuchtig.com>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pyrite
import os

if os.getenv('PYTPROF'):
    import cProfile
    import pstats
    
    cProfile.run('pyrite.run()', 'pyt-profile')
    
    p = pstats.Stats('pyt-profile')
    p.sort_stats(os.getenv('PYTPROFSORT', default='cumulative'))
    p.print_title()
    p.print_stats()
    p.print_callers()
else:
    pyrite.run()
