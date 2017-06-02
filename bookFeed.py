#!/usr/bin/python

books = []
quoteIDs = []
startingID = 10001
lastID = startingID

class Quote(object):

    def __init__(self,ticker,size,price,side):
        global lastID
        self.ticker = ticker
        self.size = size
        self.price = price
        self.side = side
        self.ID = lastID + 1
        lastID = self.ID

class Book(object):
    def __init__(self,ticker=None):
        self.book = book
        self.ticker = ticker
        self.state = 'NORMAL' # CROSSED, AUCTION etc
        self.depth = 0 # Get from levels
        self.book = []


    def addQuote(self,quote):
         assert type(quote) == Quote
         self.book.append(quote)

    def view(self,maxLevels=None):

        bids = sorted([b for b in self.book if b.side == 'B'], key=lambda quote: quote.price, reverse=True)
        asks = sorted([a for a in self.book if a.side == 'S'], key=lambda quote: quote.price)

        bookDepth = max(len(asks),len(bids))

        print '---------%s----------'
        for i in range(0,bookDepth):
            if maxLevels is not None and i > maxLevels-1: # account for zero indexing
                continue
            if i < len(bids) and i < len(asks):
                bid = bids[i]
                ask = asks[i]
                print '%d %f : %f %d' % (bid.size,bid.price,ask.price,ask.size)
            elif i > len(asks)-1:
                bid = bids[i]
                print '%d %f : None None' % (bid.size,bid.price)
            elif i > len(bids)-1:
                ask = asks[i]
                print 'None None : %f %d' % (ask.price,ask.size)



    def removeQuote(self,quoteID):
        for q in book:
            if q.ID == quoteID:
                book.remove(q)

    def execute(self,quoteID):
        print 'Trade %s of size %d at %f' % ()


def getBook(ticker):
    b = [b for b in books if b.ticker == ticker]
    assert len(b) == 1,'Found more than one book....'
    return b[0]

Quote('VODl',100,19.9,'B')
Quote('VODl',100,19.8,'B')
Quote('VODl',100,20.0,'S')
Quote('VODl',100,20.1,'S')
Quote('VODl',100,20.2,'S')
Quote('VODl',100,20.3,'S')

Quote('VODl',100,19.6,'B')
Quote('VODl',100,19.7,'B')

vodBook = Book(book)
vodBook.view()
Quote('VODl',100,19.1,'B')
vodBook.view()
vodBook.removeQuote(10007)

vodBook.view()
vodBook.removeQuote(10005)
vodBook.view()
vodBook.removeQuote(10004)
vodBook.view()
