# coding=utf-8
'''
Created on 12/07/2014

#Author: Adastra.
#twitter: @jdaanial

HiddenSitePage.py

HiddenSitePage is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

HiddenSitePage is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Tortazo; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

from scrapy.item import Item, Field

class HiddenSitePage(Item):
    title = Field()
    url = Field()
    pageParent = Field()
    pages = Field()
    imagesSrc = Field()
    forms = Field()
    body = Field()
    headers = Field()

    #Fields used for Images PipeLine. http://doc.scrapy.org/en/latest/topics/images.html
    image_urls = Field()
    images = Field()