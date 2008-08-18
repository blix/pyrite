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

from datetime import datetime

def indent(item):
    if item.__class__ == ''.__class__:
        item = item.replace('\n', '\n   ')
        item = '   ' + item
        return item
    else:
        buf = ['   ' + line for line in item]
        return buf

def humandate(timestamp):
    t = int(timestamp)
    utc = datetime.utcfromtimestamp(t)
    return utc.strftime('%a, %d %b %Y %H:%M:%S')

def shortdate(timestamp):
    d = datetime.utcfromtimestamp(int(timestamp))
    return d.strftime('%Y-%m-%d')

def relative_date(timestamp, onlyshort=True):
    n = datetime.utcnow()
    d = datetime.utcfromtimestamp(int(timestamp))
    delta = n - d
    if delta.days > 360 and onlyshort:
        return shortdate(timestamp)

    if delta.days > 365:
        return _('%d years ago') % (delta.days // 365)
    if delta.days > 30:
        return _('%d months ago') % (delta.days // 30)
    if delta.days > 7:
        return _('%d weeks ago') % (delta.days // 7)
    if delta.days:
        return _('%d days ago') % delta.days
    if delta.seconds > 60*60:
        return _('%d hours ago') % (delta.seconds // (60*60))
    if delta.seconds > 60:
        return _('%d minutes ago') % (delta.seconds // 60)
    return _('%d seconds ago') % delta.seconds

def isodate(timestamp):
    d = datetime.utcfromtimestamp(int(timestamp))
    return d.isoformat()

def ctimedate(timestamp):
    d = datetime.utcfromtimestamp(int(timestamp))
    return d.ctime()
