from .worldzero import WorldZero


async def setup(bot):
    await bot.add_cog(WorldZero(bot))
