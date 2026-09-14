from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cinema.models import Movie, Genre

class Command(BaseCommand):
    help = 'Load sample movie metadata and remote artwork; does not create users or ratings.'
    def handle(self,*args,**options):
        rows = [
            ('Dune: Part Two',2024,166,'Denis Villeneuve','Timothée Chalamet, Zendaya, Rebecca Ferguson','Long live the fighters.','Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family. Facing a choice between love and the fate of the universe, he must prevent a terrible future only he can foresee.',['Science Fiction','Adventure'],'1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg','8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg','Way9Dexny3w'),
            ('Interstellar',2014,169,'Christopher Nolan','Matthew McConaughey, Anne Hathaway, Jessica Chastain','Go further.','A team of explorers travels beyond this galaxy to discover whether mankind has a future among the stars.',['Science Fiction','Drama'],'gEU2QniE6E77NI6lCU6MxlNBvIx.jpg','xJHokMbljvjADYdit5fK5VQsXEG.jpg','zSWdZVtXT7E'),
            ('The Batman',2022,176,'Matt Reeves','Robert Pattinson, Zoë Kravitz, Jeffrey Wright','Unmask the truth.','When a killer targets Gotham’s elite, Batman follows a trail of cryptic clues into the city’s hidden corruption.',['Thriller','Action'],'74xTEgt7R36Fpooo50r9T25onhq.jpg','b0PlSFdDwbyK0cf5RxwDpaOJQvQ.jpg','mqqft2x_Aa4'),
            ('Oppenheimer',2023,180,'Christopher Nolan','Cillian Murphy, Emily Blunt, Robert Downey Jr.','The world forever changes.','Physicist J. Robert Oppenheimer leads the Manhattan Project, confronting the consequences of a discovery that changes history.',['Drama','History'],'ptpr0kGAckfQkJeJIt8st5dglvd.jpg','fm6KqXpk3M2HVveHwCrBSSBaO0V.jpg','uYPbbksJxIg'),
            ('Spider-Man: Across the Spider-Verse',2023,140,'Joaquim Dos Santos, Kemp Powers, Justin K. Thompson','Shameik Moore, Hailee Steinfeld, Oscar Isaac','It’s how you wear the mask that matters.','Miles Morales travels across the multiverse and encounters a team of Spider-People charged with protecting its existence.',['Animation','Adventure'],'8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg','4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg','cqGjhVJWtEg'),
            ('Poor Things',2023,141,'Yorgos Lanthimos','Emma Stone, Mark Ruffalo, Willem Dafoe','A world to discover.','Brought back to life by an unconventional scientist, Bella Baxter embarks on a journey of discovery and independence.',['Drama','Fantasy'],'kCGlIMHnOm8JPXq3rXM6c5wMxcT.jpg','zh6IdheEYinU4TPtorWsjx6qPQE.jpg','RlbR5N6veqw'),
        ]
        for title,year,runtime,director,cast,tagline,synopsis,genres,poster,backdrop,youtube in rows:
            movie,created = Movie.objects.get_or_create(slug=slugify(title),defaults=dict(title=title,year=year,runtime=runtime,director=director,cast=cast,tagline=tagline,synopsis=synopsis,country='United States',age_rating='R' if title in ['Oppenheimer','Poor Things'] else 'PG-13',poster_url='https://image.tmdb.org/t/p/w500/'+poster,backdrop_url='https://image.tmdb.org/t/p/w1280/'+backdrop,youtube_url='https://www.youtube.com/watch?v='+youtube,featured=title=='Dune: Part Two'))
            if created:
                movie.genres.set([Genre.objects.get_or_create(slug=slugify(g),defaults={'name':g})[0] for g in genres])
        self.stdout.write(self.style.SUCCESS('Demo catalog ready. Existing movies preserved.'))
