// Get Errors
db.getCollection('nsq_message_cache').find({
    "date" : {
        "$gte" : ISODate(new Date().toISOString().slice(0, 10))
    },
    e: { $exists: true, $eq: "Error" }
})

// Export import colleciton
// mongoexport --host mdb1r1s1.sravz.com  --port 26000 --username admin  --password PASSWORDHERE --ssl --sslAllowInvalidCertificates --authenticationDatabase=admin --db sravz_historical --collection ${item} --type=csv --out ${item}.csv
// mongoexport --host mdb1r1s1.sravz.com  --port 26000 --username admin  --password PASSWORDHERE --ssl --sslAllowInvalidCertificates --authenticationDatabase=admin --db sravz_historical --collection ${item} --type=csv --out ${item}.csv

db.getCollection('rss_feeds').createIndex(
    {
        "id": 1
    },
    {
        unique: true,
    }
  )

  // Collection size in MB
  db.getCollection('rss_feeds').stats({ scale : 1024*1024 } )

  // Get WIP messages
  db.getCollection('messages_wip').find({
    //"date" : {
    //    "$gte" : ISODate(new Date().toISOString().slice(0, 10))
    //},
    //exception_message: { $exists: true },
    'msg.id': { $exists: true, $eq: 23 }
})

// DB Stats in GB
db.stats(1024*1024*1024)

//db.getCollection('quotes_mortgage').find({})
db.getCollection('quotes_mortgage').deleteMany( { Time : {"$lt" : new Date(2021, 6, 25) } })

// Like command
db.getCollection('earnings').find({'report_date':  {
    "$eq" : ISODate(new Date().toISOString().slice(0, 10))
}, 'code': /.US/}).limit(5)


db.getCollection('assets_crypto').remove( { SravzId : { $nin: ['crypto_btc_usd', 'crypto_eth_usd', 'crypto_usdt_usd', 'crypto_bnb_usd', 'crypto_doge_usd'] } } )

db.getCollection('rss_feeds').deleteMany( { datetime : {"$lt" : new Date(2024, 12, 31) } })
db.getCollection('nsq_message_cache').deleteMany( { orderExpDate : {"$lt" : new Date(Date.now() - 2*24*60*60 * 1000) } })

// Get cron messages
db.getCollection('nsq_message_cache').find({
    "date" : {
        "$gte" : ISODate(new Date().toISOString().slice(0, 10))
    },
    e: { $exists: true, $eq: "Error" },
    id: {$gte:23,$lt:49},
})
