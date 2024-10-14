# Generated by Django 4.2.13 on 2024-08-05 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wod20th", "0018_stat_instanced"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stat",
            name="category",
            field=models.CharField(
                choices=[
                    ("attributes", "Attributes"),
                    ("abilities", "Abilities"),
                    ("advantages", "Advantages"),
                    ("backgrounds", "Backgrounds"),
                    ("powers", "Powers"),
                    {"merits", "Merits"},
                    ("flaws", "Flaws"),
                    ("traits", "Traits"),
                    ("identity", "Identity"),
                    ("virtues", "Virtues"),
                    ("pools", "Pools"),
                    ("other", "Other"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="stat",
            name="stat_type",
            field=models.CharField(
                choices=[
                    ("attribute", "Attribute"),
                    ("ability", "Ability"),
                    ("advantage", "Advantage"),
                    ("background", "Background"),
                    ("lineage", "Lineage"),
                    ("discipline", "Discipline"),
                    ("gift", "Gift"),
                    ("sphere", "Sphere"),
                    ("rote", "Rote"),
                    ("art", "Art"),
                    ("edge", "Edge"),
                    ("discipline", "Discipline"),
                    ("path", "Path"),
                    ("power", "Power"),
                    ("other", "Other"),
                    ("virtue", "Virtue"),
                    ("vice", "Vice"),
                    ("merit", "Merit"),
                    ("flaw", "Flaw"),
                    ("trait", "Trait"),
                    ("skill", "Skill"),
                    ("knowledge", "Knowledge"),
                    ("talent", "Talent"),
                    ("specialty", "Specialty"),
                    ("other", "Other"),
                    ("physical", "Physical"),
                    ("social", "Social"),
                    ("mental", "Mental"),
                    ("personal", "Personal"),
                    ("supernatural", "Supernatural"),
                    ("moral", "Moral"),
                    ("inhuman", "Inhuman"),
                    ("temporary", "Temporary"),
                    ("other", "Other"),
                ],
                max_length=100,
            ),
        ),
    ]
