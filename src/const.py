"""EVE constants.

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Part of this code is inspired by or based on EVE Online.
Used with permission from CCP.
"""

ACT_IDX_START = 0
ACT_IDX_DURATION = 1
ACT_IDX_ENV = 2
ACT_IDX_REPEAT = 3

dgmAssPreAssignment = -1
dgmAssPreMul = 0
dgmAssPreDiv = 1
dgmAssModAdd = 2
dgmAssModSub = 3
dgmAssPostMul = 4
dgmAssPostDiv = 5
dgmAssPostPercent = 6
dgmAssPostAssignment = 7

dgmEnvSelf = 0
dgmEnvChar = 1
dgmEnvShip = 2
dgmEnvTarget = 3
dgmEnvOther = 4
dgmEnvArea = 5

dgmEffActivation = 1
dgmEffArea = 3
dgmEffOnline = 4
dgmEffPassive = 0
dgmEffTarget = 2
dgmEffOverload = 5
dgmEffDungeon = 6
dgmEffSystem = 7

dgmTauConstant = 10000

flagAutoFit = 0
flagBonus = 86
flagBooster = 88
flagBriefcase = 6
flagCapsule = 56
flagCargo = 5
flagCorpMarket = 62
flagCorpSAG2 = 116
flagCorpSAG3 = 117
flagCorpSAG4 = 118
flagCorpSAG5 = 119
flagCorpSAG6 = 120
flagCorpSAG7 = 121
flagDroneBay = 87
flagFactoryOperation = 100
flagFixedSlot = 35
flagHangar = 4
flagHangarAll = 1000
flagHiSlot0 = 27
flagHiSlot1 = 28
flagHiSlot2 = 29
flagHiSlot3 = 30
flagHiSlot4 = 31
flagHiSlot5 = 32
flagHiSlot6 = 33
flagHiSlot7 = 34
flagImplant = 89
flagLoSlot0 = 11
flagLoSlot7 = 18
flagLocked = 63
flagMedSlot0 = 19
flagMedSlot7 = 26
flagNone = 0
flagPilot = 57
flagReward = 8
flagRigSlot0 = 92
flagRigSlot1 = 93
flagRigSlot2 = 94
flagRigSlot3 = 95
flagRigSlot4 = 96
flagRigSlot5 = 97
flagRigSlot6 = 98
flagRigSlot7 = 99
flagSecondaryStorage = 122
flagShipHangar = 90
flagShipOffline = 91
flagSkill = 7
flagSkillInTraining = 61
flagSlotFirst = 11
flagSlotLast = 35
flagSubSystemSlot0 = 125
flagSubSystemSlot1 = 126
flagSubSystemSlot2 = 127
flagSubSystemSlot3 = 128
flagSubSystemSlot4 = 129
flagSubSystemSlot5 = 130
flagSubSystemSlot6 = 131
flagSubSystemSlot7 = 132
flagUnlocked = 64
flagWallet = 1
flagJunkyardReprocessed = 146
flagJunkyardTrashed = 147
flagWardrobe = 3

categoryAbstract = 29
categoryAccessories = 5
categoryAncientRelic = 34
categoryApparel = 30
categoryAsteroid = 25
categoryWorldSpace = 26
categoryBlueprint = 9
categoryBonus = 14
categoryCelestial = 2
categoryCharge = 8
categoryCommodity = 17
categoryDecryptors = 35
categoryDeployable = 22
categoryDrone = 18
categoryEntity = 11
categoryImplant = 20
categoryMaterial = 4
categoryModule = 7
categoryOrbital = 46
categoryOwner = 1
categoryPlaceables = 49
categoryPlanetaryCommodities = 43
categoryPlanetaryInteraction = 41
categoryPlanetaryResources = 42
categoryReaction = 24
categoryShip = 6
categorySkill = 16
categorySovereigntyStructure = 40
categoryStation = 3
categoryStructure = 23
categoryStructureUpgrade = 39
categorySubSystem = 32
categorySystem = 0
categoryTrading = 10


# Inventory constants - groups
groupAccelerationGateKeys = 474
groupAfterBurner = 46 
groupAgentsinSpace = 517
groupAlliance = 32
groupAmmo = 83
groupArkonor = 450
groupArmorReinforcer = 329
groupArmorRepairUnit = 62 
groupAssemblyArray = 397
groupAsteroidAngelCartelBattleCruiser = 576
groupAsteroidAngelCartelBattleship = 552
groupAsteroidAngelCartelCommanderBattleCruiser = 793
groupAsteroidAngelCartelCommanderCruiser = 790
groupAsteroidAngelCartelCommanderDestroyer = 794
groupAsteroidAngelCartelCommanderFrigate = 789
groupAsteroidAngelCartelCruiser = 551
groupAsteroidAngelCartelDestroyer = 575
groupAsteroidAngelCartelFrigate = 550
groupAsteroidAngelCartelHauler = 554
groupAsteroidAngelCartelOfficer = 553
groupAsteroidBelt = 9
groupAsteroid = 25
groupAsteroidBloodRaidersBattleCruiser = 578
groupAsteroidBloodRaidersBattleship = 556
groupAsteroidBloodRaidersCommanderBattleCruiser = 795
groupAsteroidBloodRaidersCommanderCruiser = 791
groupAsteroidBloodRaidersCommanderDestroyer = 796
groupAsteroidBloodRaidersCommanderFrigate = 792
groupAsteroidBloodRaidersCruiser = 555
groupAsteroidBloodRaidersDestroyer = 577
groupAsteroidBloodRaidersFrigate = 557
groupAsteroidBloodRaidersHauler = 558
groupAsteroidBloodRaidersOfficer = 559
groupAsteroidGuristasBattleCruiser = 580
groupAsteroidGuristasBattleship = 560
groupAsteroidGuristasCommanderBattleCruiser = 797
groupAsteroidGuristasCommanderCruiser = 798
groupAsteroidGuristasCommanderDestroyer = 799
groupAsteroidGuristasCommanderFrigate = 800
groupAsteroidGuristasCruiser = 561
groupAsteroidGuristasDestroyer = 579
groupAsteroidGuristasFrigate = 562
groupAsteroidGuristasHauler = 563
groupAsteroidGuristasOfficer = 564
groupAsteroidRogueDroneBattleCruiser = 755
groupAsteroidRogueDroneBattleship = 756
groupAsteroidRogueDroneCruiser = 757
groupAsteroidRogueDroneDestroyer = 758
groupAsteroidRogueDroneFrigate = 759
groupAsteroidRogueDroneHauler = 760
groupAsteroidRogueDroneSwarm = 761
groupAsteroidSanshasNationBattleCruiser = 582
groupAsteroidSanshasNationBattleship = 565
groupAsteroidSanshasNationCommanderBattleCruiser = 807
groupAsteroidSanshasNationCommanderCruiser = 808
groupAsteroidSanshasNationCommanderDestroyer = 809
groupAsteroidSanshasNationCommanderFrigate = 810
groupAsteroidSanshasNationCruiser = 566
groupAsteroidSanshasNationDestroyer = 581
groupAsteroidSanshasNationFrigate = 567
groupAsteroidSanshasNationHauler = 568
groupAsteroidSanshasNationOfficer = 569
groupAsteroidSerpentisBattleCruiser = 584
groupAsteroidSerpentisBattleship = 570
groupAsteroidSerpentisCommanderBattleCruiser = 811
groupAsteroidSerpentisCommanderCruiser = 812
groupAsteroidSerpentisCommanderDestroyer = 813
groupAsteroidSerpentisCommanderFrigate = 814
groupAsteroidSerpentisCruiser = 571
groupAsteroidSerpentisDestroyer = 583
groupAsteroidSerpentisFrigate = 572
groupAsteroidSerpentisHauler = 573
groupAsteroidSerpentisOfficer = 574
groupAsteroidRogueDroneCommanderFrigate = 847
groupAsteroidRogueDroneCommanderDestroyer = 846
groupAsteroidRogueDroneCommanderCruiser = 845
groupAsteroidRogueDroneCommanderBattleCruiser = 843
groupAsteroidRogueDroneCommanderBattleship = 844
groupAsteroidAngelCartelCommanderBattleship = 848
groupAsteroidBloodRaidersCommanderBattleship = 849
groupAsteroidGuristasCommanderBattleship = 850
groupAsteroidSanshasNationCommanderBattleship = 851
groupAsteroidSerpentisCommanderBattleship = 852
groupMissionAmarrEmpireCarrier = 865
groupMissionCaldariStateCarrier = 866
groupMissionContainer = 952
groupMissionGallenteFederationCarrier = 867
groupMissionMinmatarRepublicCarrier = 868
groupMissionFighterDrone = 861
groupMissionGenericFreighters = 875

groupAccelerationGateKeys = 474
groupAfterBurner = 46
groupAgentsinSpace = 517
groupAlliance = 32
groupAncientCompressedIce = 903
groupAncientSalvage = 966
groupArkonor = 450
groupArmorReinforcer = 329
groupArmorRepairUnit = 62
groupAssemblyArray = 397
groupAsteroidAngelCartelBattleCruiser = 576
groupAsteroidAngelCartelBattleship = 552
groupAsteroidAngelCartelCommanderBattleCruiser = 793
groupAsteroidAngelCartelCommanderCruiser = 790
groupAsteroidAngelCartelCommanderDestroyer = 794
groupAsteroidAngelCartelCommanderFrigate = 789
groupAsteroidAngelCartelCruiser = 551
groupAsteroidAngelCartelDestroyer = 575
groupAsteroidAngelCartelFrigate = 550
groupAsteroidAngelCartelHauler = 554
groupAsteroidAngelCartelOfficer = 553
groupAsteroidBelt = 9
groupAsteroid = 25
groupAsteroidBloodRaidersBattleCruiser = 578
groupAsteroidBloodRaidersBattleship = 556
groupAsteroidBloodRaidersCommanderBattleCruiser = 795
groupAsteroidBloodRaidersCommanderCruiser = 791
groupAsteroidBloodRaidersCommanderDestroyer = 796
groupAsteroidBloodRaidersCommanderFrigate = 792
groupAsteroidBloodRaidersCruiser = 555
groupAsteroidBloodRaidersDestroyer = 577
groupAsteroidBloodRaidersFrigate = 557
groupAsteroidBloodRaidersHauler = 558
groupAsteroidBloodRaidersOfficer = 559
groupAsteroidGuristasBattleCruiser = 580
groupAsteroidGuristasBattleship = 560
groupAsteroidGuristasCommanderBattleCruiser = 797
groupAsteroidGuristasCommanderCruiser = 798
groupAsteroidGuristasCommanderDestroyer = 799
groupAsteroidGuristasCommanderFrigate = 800
groupAsteroidGuristasCruiser = 561
groupAsteroidGuristasDestroyer = 579
groupAsteroidGuristasFrigate = 562
groupAsteroidGuristasHauler = 563
groupAsteroidGuristasOfficer = 564
groupAsteroidRogueDroneBattleCruiser = 755
groupAsteroidRogueDroneBattleship = 756
groupAsteroidRogueDroneCruiser = 757
groupAsteroidRogueDroneDestroyer = 758
groupAsteroidRogueDroneFrigate = 759
groupAsteroidRogueDroneHauler = 760
groupAsteroidRogueDroneSwarm = 761
groupAsteroidSanshasNationBattleCruiser = 582
groupAsteroidSanshasNationBattleship = 565
groupAsteroidSanshasNationCommanderBattleCruiser = 807
groupAsteroidSanshasNationCommanderCruiser = 808
groupAsteroidSanshasNationCommanderDestroyer = 809
groupAsteroidSanshasNationCommanderFrigate = 810
groupAsteroidSanshasNationCruiser = 566
groupAsteroidSanshasNationDestroyer = 581
groupAsteroidSanshasNationFrigate = 567
groupAsteroidSanshasNationHauler = 568
groupAsteroidSanshasNationOfficer = 569
groupAsteroidSerpentisBattleCruiser = 584
groupAsteroidSerpentisBattleship = 570
groupAsteroidSerpentisCommanderBattleCruiser = 811
groupAsteroidSerpentisCommanderCruiser = 812
groupAsteroidSerpentisCommanderDestroyer = 813
groupAsteroidSerpentisCommanderFrigate = 814
groupAsteroidSerpentisCruiser = 571
groupAsteroidSerpentisDestroyer = 583
groupAsteroidSerpentisFrigate = 572
groupAsteroidSerpentisHauler = 573
groupAsteroidSerpentisOfficer = 574
groupAsteroidRogueDroneCommanderFrigate = 847
groupAsteroidRogueDroneCommanderDestroyer = 846
groupAsteroidRogueDroneCommanderCruiser = 845
groupAsteroidRogueDroneCommanderBattleCruiser = 843
groupAsteroidRogueDroneCommanderBattleship = 844
groupAsteroidAngelCartelCommanderBattleship = 848
groupAsteroidBloodRaidersCommanderBattleship = 849
groupAsteroidGuristasCommanderBattleship = 850
groupAsteroidSanshasNationCommanderBattleship = 851
groupAsteroidSerpentisCommanderBattleship = 852
groupMissionAmarrEmpireCarrier = 865
groupMissionCaldariStateCarrier = 866
groupMissionContainer = 952
groupMissionGallenteFederationCarrier = 867
groupMissionMinmatarRepublicCarrier = 868
groupMissionFighterDrone = 861
groupMissionGenericFreighters = 875
groupAssaultShip = 324
groupAuditLogSecureContainer = 448
groupBattlecruiser = 419
groupBattleship = 27
groupBeacon = 310
groupBillboard = 323
groupBiohazard = 284
groupBiomass = 14
groupBistot = 451
groupBlackOps = 898
groupBomb = 90
groupBombECM = 863
groupBombEnergy = 864
groupBooster = 303
groupBubbleProbeLauncher = 589
groupCapDrainDrone = 544
groupCapacitorBooster = 76
groupCapacitorBoosterCharge = 87
groupCapitalIndustrialShip = 883
groupCapsule = 29
groupCapturePointTower = 922
groupCargoContainer = 12
groupCarrier = 547
groupCharacter = 1
groupCheatModuleGroup = 225
groupCitadelTorpedo = 476
groupCloakingDevice = 330
groupClone = 23
groupCloud = 227
groupCombatDrone = 100
groupComet = 305
groupCommandPins = 1027
groupCommandShip = 540
groupComposite = 429
groupComputerInterfaceNode = 317
groupConcordDrone = 301
groupConstellation = 4
groupConstructionPlatform = 307
groupControlBunker = 925
groupControlTower = 365
groupConvoy = 297
groupConvoyDrone = 298
groupCorporateHangarArray = 471
groupCorporation = 2
groupCosmicAnomaly = 885
groupCosmicSignature = 502
groupCovertBeacon = 897
groupCovertOps = 830
groupCrokite = 452
groupCruiser = 26
groupStrategicCruiser = 963
groupCustomsOfficial = 446
groupCynosuralGeneratorArray = 838
groupCynosuralSystemJammer = 839
groupDarkOchre = 453
groupDataInterfaces = 716
groupDatacores = 333
groupDeadspaceAngelCartelBattleCruiser = 593
groupDeadspaceAngelCartelBattleship = 594
groupDeadspaceAngelCartelCruiser = 595
groupDeadspaceAngelCartelDestroyer = 596
groupDeadspaceAngelCartelFrigate = 597
groupDeadspaceBloodRaidersBattleCruiser = 602
groupDeadspaceBloodRaidersBattleship = 603
groupDeadspaceBloodRaidersCruiser = 604
groupDeadspaceBloodRaidersDestroyer = 605
groupDeadspaceBloodRaidersFrigate = 606
groupDeadspaceGuristasBattleCruiser = 611
groupDeadspaceGuristasBattleship = 612
groupDeadspaceGuristasCruiser = 613
groupDeadspaceGuristasDestroyer = 614
groupDeadspaceGuristasFrigate = 615
groupDeadspaceOverseer = 435
groupDeadspaceOverseersBelongings = 496
groupDeadspaceOverseersSentry = 495
groupDeadspaceOverseersStructure = 494
groupDeadspaceRogueDroneBattleCruiser = 801
groupDeadspaceRogueDroneBattleship = 802
groupDeadspaceRogueDroneCruiser = 803
groupDeadspaceRogueDroneDestroyer = 804
groupDeadspaceRogueDroneFrigate = 805
groupDeadspaceRogueDroneSwarm = 806
groupDeadspaceSanshasNationBattleCruiser = 620
groupDeadspaceSanshasNationBattleship = 621
groupDeadspaceSanshasNationCruiser = 622
groupDeadspaceSanshasNationDestroyer = 623
groupDeadspaceSanshasNationFrigate = 624
groupDeadspaceSerpentisBattleCruiser = 629
groupDeadspaceSerpentisBattleship = 630
groupDeadspaceSerpentisCruiser = 631
groupDeadspaceSerpentisDestroyer = 632
groupDeadspaceSerpentisFrigate = 633
groupDeadspaceSleeperSleeplessPatroller = 983
groupDeadspaceSleeperSleeplessSentinel = 959
groupDeadspaceSleeperSleeplessDefender = 982
groupDeadspaceSleeperAwakenedPatroller = 985
groupDeadspaceSleeperAwakenedSentinel = 960
groupDeadspaceSleeperAwakenedDefender = 984
groupDeadspaceSleeperEmergentPatroller = 987
groupDeadspaceSleeperEmergentSentinel = 961
groupDeadspaceSleeperEmergentDefender = 986
groupDefenderMissile = 88
groupDefenseBunkers = 1004
groupDestroyer = 420
groupDestructibleAgentsInSpace = 715
groupDestructibleSentryGun = 383
groupDestructibleStationServices = 874
groupDreadnought = 485
groupEffectBeacon = 920
groupElectronicWarfareBattery = 439
groupElectronicWarfareDrone = 639
groupEliteBattleship = 381
groupEnergyNeutralizingBattery = 837
groupEnergyWeapon = 53
groupEnergyVampire = 68
groupExhumer = 543
groupExtractionControlUnitPins = 1063
groupExtractorPins = 1026
groupFaction = 19
groupFactionDrone = 288
groupFakeSkills = 505
groupFighterBomber = 1023
groupFighterDrone = 549
groupFlashpoint = 1071
groupForceField = 411
groupForceFieldArray = 445
groupFreightContainer = 649
groupFreighter = 513
groupFrequencyCrystal = 86
groupFrequencyMiningLaser = 483
groupFrigate = 25
groupFrozen = 281
groupGasCloudHarvester = 737
groupGasIsotopes = 422
groupGeneral = 280
groupGlobalWarpDisruptor = 368
groupGneiss = 467
groupHarvestableCloud = 711
groupHeavyAssaultShip = 358
groupHedbergite = 454
groupHemorphite = 455
groupHullRepairUnit = 63
groupHybridAmmo = 85
groupHybridWeapon = 74
groupIce = 465
groupIceProduct = 423
groupImpactor = 1070
groupIndustrial = 28
groupIndustrialCommandShip = 941
groupInfrastructureHub = 1012
groupInterceptor = 831
groupInterdictor = 541
groupIntermediateMaterials = 428
groupInvasionSanshaNationBattleship = 1056
groupInvasionSanshaNationCapital = 1052
groupInvasionSanshaNationCruiser = 1054
groupInvasionSanshaNationFrigate = 1053
groupInvasionSanshaNationIndustrial = 1051
groupJaspet = 456
groupJumpPortalArray = 707
groupJumpPortalGenerator = 590
groupKernite = 457
groupLCODrone = 279
groupLandmark = 318
groupLargeCollidableObject = 226
groupLargeCollidableShip = 784
groupLargeCollidableStructure = 319
groupLearning = 267
groupLease = 652
groupLivestock = 283
groupLogisticDrone = 640
groupLogistics = 832
groupLogisticsArray = 710
groupMercoxit = 468
groupMine = 92
groupMineral = 18
groupMiningBarge = 463
groupMiningDrone = 101
groupMiningLaser = 54
groupMissile = 84
groupMissileLauncher = 56
groupMissileLauncherAssault = 511
groupMissileLauncherBomb = 862
groupMissileLauncherCitadel = 524
groupMissileLauncherCruise = 506
groupMissileLauncherDefender = 512
groupMissileLauncherHeavy = 510
groupMissileLauncherHeavyAssault = 771
groupMissileLauncherRocket = 507
groupMissileLauncherSiege = 508
groupMissileLauncherSnowball = 501
groupMissileLauncherStandard = 509
groupMissionAmarrEmpireBattlecruiser = 666
groupMissionAmarrEmpireBattleship = 667
groupMissionAmarrEmpireCruiser = 668
groupMissionAmarrEmpireDestroyer = 669
groupMissionAmarrEmpireFrigate = 665
groupMissionAmarrEmpireOther = 670
groupMissionCONCORDBattlecruiser = 696
groupMissionCONCORDBattleship = 697
groupMissionCONCORDCruiser = 695
groupMissionCONCORDDestroyer = 694
groupMissionCONCORDFrigate = 693
groupMissionCONCORDOther = 698
groupMissionCaldariStateBattlecruiser = 672
groupMissionCaldariStateBattleship = 674
groupMissionCaldariStateCruiser = 673
groupMissionCaldariStateDestroyer = 676
groupMissionCaldariStateFrigate = 671
groupMissionCaldariStateOther = 675
groupMissionDrone = 337
groupMissionFactionBattleships = 924
groupMissionFactionCruisers = 1006
groupMissionFactionFrigates = 1007
groupMissionFactionIndustrials = 927
groupMissionGallenteFederationBattlecruiser = 681
groupMissionGallenteFederationBattleship = 680
groupMissionGallenteFederationCruiser = 678
groupMissionGallenteFederationDestroyer = 679
groupMissionGallenteFederationFrigate = 677
groupMissionGallenteFederationOther = 682
groupMissionKhanidBattlecruiser = 690
groupMissionKhanidBattleship = 691
groupMissionKhanidCruiser = 689
groupMissionKhanidDestroyer = 688
groupMissionKhanidFrigate = 687
groupMissionKhanidOther = 692
groupMissionMinmatarRepublicBattlecruiser = 685
groupMissionMinmatarRepublicBattleship = 706
groupMissionMinmatarRepublicCruiser = 705
groupMissionMinmatarRepublicDestroyer = 684
groupMissionMinmatarRepublicFrigate = 683
groupMissionMinmatarRepublicOther = 686
groupMissionMorduBattlecruiser = 702
groupMissionMorduBattleship = 703
groupMissionMorduCruiser = 701
groupMissionMorduDestroyer = 700
groupMissionMorduFrigate = 699
groupMissionMorduOther = 704
groupMobileHybridSentry = 449
groupMobileLaboratory = 413
groupMobileLaserSentry = 430
groupMobileMissileSentry = 417
groupTransportShip = 380
groupJumpFreighter = 902
groupMobilePowerCore = 414
groupMobileProjectileSentry = 426
groupMobileReactor = 438
groupMobileSentryGun = 336
groupMobileShieldGenerator = 418
groupMobileStorage = 364
groupMobileWarpDisruptor = 361
groupMoney = 17
groupMoon = 8
groupMoonMaterials = 427
groupMoonMining = 416
groupSupercarrier = 659
groupOmber = 469
groupOverseerPersonalEffects = 493
groupOutpostImprovements = 872
groupOutpostUpgrades = 876
groupPirateDrone = 185
groupPlagioclase = 458
groupPlanet = 7
groupPlanetaryCustomsOffices = 1025
groupPlanetaryCloud = 312
groupPlanetaryLinks = 1036
groupPoliceDrone = 182
groupProcessPins = 1028
groupProjectileAmmo = 83
groupProjectileWeapon = 55
groupTractorBeam = 650
groupProtectiveSentryGun = 180
groupPrototypeExplorationShip = 1022
groupProximityDrone = 97
groupPyroxeres = 459
groupRadioactive = 282
groupForceReconShip = 833
groupCombatReconShip = 906
groupRefinables = 355
groupRefiningArray = 311
groupRegion = 3
groupRemoteSensorBooster = 290
groupRemoteSensorDamper = 208
groupRepairDrone = 299
groupRing = 13
groupRogueDrone = 287
groupRookieship = 237
groupSalvagedMaterials = 754
groupScanProbeLauncher = 481
groupScannerArray = 709
groupScannerProbe = 479
groupScordite = 460
groupSecureCargoContainer = 340
groupSensorBooster = 212
groupSensorDampeningBattery = 440
groupSentryGun = 99
groupShieldBooster = 40
groupShieldHardeningArray = 444
groupShipMaintenanceArray = 363
groupShippingCrates = 382
groupShuttle = 31
groupSiegeModule = 515
groupSilo = 404
groupSolarSystem = 5
groupSovereigntyClaimMarkers = 1003
groupSovereigntyDisruptionStructures = 1005
groupSovereigntyStructures = 1004
groupSpaceportPins = 1030
groupSpawnContainer = 306
groupSpodumain = 461
groupStargate = 10
groupStasisWebificationBattery = 441
groupStasisWebifyingDrone = 641
groupStation = 15
groupStationServices = 16
groupStationUpgradePlatform = 835
groupStationImprovementPlatform = 836
groupStealthBomber = 834
groupStealthEmitterArray = 480
groupStoragePins = 1029
groupStorylineBattleship = 523
groupStorylineCruiser = 522
groupStorylineFrigate = 520
groupStorylineMissionBattleship = 534
groupStorylineMissionCruiser = 533
groupStorylineMissionFrigate = 527
groupStripMiner = 464
groupStructureRepairArray = 840
groupSovUpgradeIndustrial = 1020
groupSovUpgradeMilitary = 1021
groupSun = 6
groupSuperWeapon = 588
groupSurveyProbe = 492
groupSystem = 0
groupTargetPaintingBattery = 877
groupTemporaryCloud = 335
groupTestOrbitals = 1073
groupTerranArtifacts = 519
groupTitan = 30
groupTool = 332
groupTrackingArray = 473
groupTrackingComputer = 213
groupTrackingDisruptor = 291
groupTrackingLink = 209
groupTradeSession = 95
groupTrading = 94
groupTutorialDrone = 286
groupUnanchoringDrone = 470
groupVeldspar = 462
groupVoucher = 24
groupWarpDisruptFieldGenerator = 899
groupWarpDisruptionProbe = 548
groupWarpGate = 366
groupWarpScramblingBattery = 443
groupWarpScramblingDrone = 545
groupWreck = 186
groupZombieEntities = 934
groupMissionGenericBattleships = 816
groupMissionGenericCruisers = 817
groupMissionGenericFrigates = 818
groupMissionThukkerBattlecruiser = 822
groupMissionThukkerBattleship = 823
groupMissionThukkerCruiser = 824
groupMissionThukkerDestroyer = 825
groupMissionThukkerFrigate = 826
groupMissionThukkerOther = 827
groupMissionGenericBattleCruisers = 828
groupMissionGenericDestroyers = 829
groupDeadspaceOverseerFrigate = 819
groupDeadspaceOverseerCruiser = 820
groupDeadspaceOverseerBattleship = 821
groupElectronicAttackShips = 893
groupEnergyNeutralizingBattery = 837
groupHeavyInterdictors = 894
groupMarauders = 900
groupDecorations = 937
groupDefensiveSubSystems = 954
groupElectronicSubSystems = 955
groupEngineeringSubSystems = 958
groupOffensiveSubSystems = 956
groupPropulsionSubSystems = 957
groupWormhole = 988
groupSecondarySun = 995
groupGameTime = 943
groupWorldSpace = 935
groupSalvager = 1122


typeTicketFrigate = 30717
typeTicketDestroyer = 30718
typeTicketBattleship = 30721
typeTicketCruiser = 30722
typeTicketBattlecruiser = 30723
typeAccounting = 16622
typeAcolyteI = 2203
typeAdvancedLaboratoryOperation = 24624
typeAdvancedMassProduction = 24625
typeAlliance = 16159
typeAmarrFreighterWreck = 26483
typeAmarrEliteFreighterWreck = 29033
typeApocalypse = 642
typeArchaeology = 13278
typeAstrometrics = 3412
typeAutomatedCentiiKeyholder = 22053
typeAutomatedCentiiTrainingVessel = 21849
typeAutomatedCoreliTrainingVessel = 21845
typeAutomatedCorpiiTrainingVessel = 21847
typeAutomatedGistiTrainingVessel = 21846
typeAutomatedPithiTrainingVessel = 21848
typeBHMegaCargoShip = 11019
typeBasicDamageControl = 521
typeBeacon = 10124
typeBiomass = 3779
typeBookmark = 51
typeBrokerRelations = 3446
typeBubbleProbeLauncher = 22782
typeBureaucraticConnections = 16546
typeCaldariFreighterWreck = 26505
typeCaldariEliteFreighterWreck = 29034
typeCapitalShips = 20533
typeCargoContainer = 23
typeCelestialAgentSiteBeacon = 25354
typeCelestialBeaconII = 19706
typeCertificate = 29530
typeCharacterAchura = 1383
typeCharacterAmarr = 1373
typeCharacterBrutor = 1380
typeCharacterCivire = 1375
typeCharacterDeteis = 1376
typeCharacterGallente = 1377
typeCharacterIntaki = 1378
typeCharacterJinMei = 1384
typeCharacterKhanid = 1385
typeCharacterModifier = 1382
typeCharacterNiKunni = 1374
typeCharacterSebiestor = 1379
typeCharacterStatic = 1381
typeCharacterVherokior = 1386
typeCloneGradeAlpha = 164
typeCloneVatBayI = 23735
typeCloningService = 28158
typeCompanyShares = 50
typeConnections = 3359
typeConstellation = 4
typeContracting = 25235
typeCorporation = 2
typeCorporationContracting = 25233
typeCorporationManagement = 3363
typeCorpse = 25
typeCorpseFemale = 29148
typeCovertCynosuralFieldI = 28650
typeCredits = 29
typeCriminalConnections = 3361
typeCrowBlueprint = 11177
typeCynosuralFieldI = 21094
typeDamageControlI = 2046
typeDaytrading = 16595
typeDeadspaceSignature = 19728
typeDefenderI = 265
typeDiplomacy = 3357
typeDoomTorpedoIBlueprint = 17864
typeDuplicating = 10298
typeDustStreak = 10756
typeElectronics = 3426
typeEmpireControl = 3732
typeEngineering = 3413
typeEthnicRelations = 3368
typeFaction = 30
typeFactoryService = 28157
typeFinancialConnections = 16547
typeFittingService = 28155
typeFleetCommand = 24764
typeForceField = 16103
typeGallenteFreighterWreck = 26527
typeGallenteEliteFreighterWreck = 29035
typeGeneralFreightContainer = 24445
typeGistiiHijacker = 16877
typeHacking = 21718
typeHangarContainer = 3298
typeHighTechConnections = 16552
typeIndustry = 3380
typeLaborConnections = 16550
typeLaboratoryOperation = 3406
typeLaboratoryService = 28166
typeLargeCryoContainer = 3464
typeLargeLifeSupportContainer = 3459
typeLargeRadiationShieldedContainer = 3461
typeLargeSecureContainer = 3465
typeLargeStandardContainer = 3296
typeLeadership = 3348
typeLoyaltyPoints = 29247
typeMapLandmark = 11367
typeMarginTrading = 16597
typeMarketing = 16598
typeMassProduction = 3387
typeMedal = 29496
typeMediumCryoContainer = 3463
typeMediumLifeSupportContainer = 3458
typeMediumRadiationShieldedContainer = 3460
typeMediumSecureContainer = 3466
typeMediumStandardContainer = 3293
typeMetallurgy = 3409
typeMilitaryConnections = 16549
typeMinmatarFreighterWreck = 26549
typeMinmatarEliteFreighterWreck = 29036
typeMissileLauncherOperation = 3319
typeMoon = 14
typeNaniteRepairPaste = 28668
typeNegotiation = 3356
typeOffice = 27
typeOfficeFolder = 26
typeOmnipotent = 19430
typePlanetGas = 13
typePlanetIce = 12
typePlanetSolid = 11
typePlanetShattered = 30889
typePlasticWrap = 3468
typePlayerKill = 49
typePolarisCenturion = 9858
typePolarisCenturionFrigate = 9862
typePolarisInspectorFrigate = 9854
typePolarisLegatusFrigate = 9860
typePoliticalConnections = 16548
typeProcurement = 16594
typeRank = 29495
typeRegion = 3
typeRepairService = 28159
typeReprocessingService = 28156
typeResearch = 3403
typeResearchProjectManagement = 12179
typeRetail = 3444
typeRibbon = 29497
typeScience = 3402
typeScientificNetworking = 24270
typeScrapmetalProcessing = 12196
typeSlaver = 12049
typeSmallCryoContainer = 3462
typeSmallLifeSupportContainer = 3295
typeSmallRadiationShieldedContainer = 3294
typeSmallSecureContainer = 3467
typeSmallStandardContainer = 3297
typeSocial = 3355
typeSoftCloud = 10753
typeSolarSystem = 5
typeSpaceAnchor = 2528
typeStationConquerable1 = 12242
typeStationConquerable2 = 12294
typeStationConquerable3 = 12295
typeStationContainer = 17366
typeStationVault = 17367
typeStationWarehouse = 17368
typeSupplyChainManagement = 24268
typeSystem = 0
typeThePrizeContainer = 19373
typeThermodynamics = 28164
typeTrade = 3443
typeTradeConnections = 16551
typeTradeSession = 53
typeTrading = 52
typeTritanium = 34
typeTycoon = 18580
typeUniverse = 9
typeVeldspar = 1230
typeVisibility = 3447
typeWarpDisruptionFocusingScript = 29003
typeWholesale = 16596
typeWingCommand = 11574
typeWispyChlorineCloud = 10758
typeWispyOrangeCloud = 10754
typeWreck = 26468
typePilotLicence = 29668
typeAsteroidBelt = 15
typeLetterOfRecommendation = 30906

accountingKeyCash = 1000
accountingKeyCash2 = 1001
accountingKeyCash3 = 1002
accountingKeyCash4 = 1003
accountingKeyCash5 = 1004
accountingKeyCash6 = 1005
accountingKeyCash7 = 1006
accountingKeyProperty = 1100
accountingKeyAUR = 1200
accountingKeyAUR2 = 1201
accountingKeyAUR3 = 1202
accountingKeyAUR4 = 1203
accountingKeyAUR5 = 1204
accountingKeyAUR6 = 1205
accountingKeyAUR7 = 1206
accountingKeyEscrow = 1500
accountingKeyReceivables = 1800
accountingKeyPayables = 2000
accountingKeyGold = 2010
accountingKeyEquity = 2900
accountingKeySales = 3000
accountingKeyPurchases = 4000
accountingKeyDustIsk = 10000
accountingKeyDustMPlex = 11000

cashAccounts = set([
 accountingKeyCash,
 accountingKeyCash2,
 accountingKeyCash3,
 accountingKeyCash4,
 accountingKeyCash5,
 accountingKeyCash6,
 accountingKeyCash7
])

aurAccounts = set([
 accountingKeyAUR,
 accountingKeyAUR2,
 accountingKeyAUR3,
 accountingKeyAUR4,
 accountingKeyAUR5,
 accountingKeyAUR6,
 accountingKeyAUR7
])

flagLoSlot0 = 11
flagLoSlot1 = 12
flagLoSlot2 = 13
flagLoSlot3 = 14
flagLoSlot4 = 15
flagLoSlot5 = 16
flagLoSlot6 = 17
flagLoSlot7 = 18
flagMedSlot0 = 19
flagMedSlot1 = 20
flagMedSlot2 = 21
flagMedSlot3 = 22
flagMedSlot4 = 23
flagMedSlot5 = 24
flagMedSlot6 = 25
flagMedSlot7 = 26
flagHiSlot0 = 27
flagHiSlot1 = 28
flagHiSlot2 = 29
flagHiSlot3 = 30
flagHiSlot4 = 31
flagHiSlot5 = 32
flagHiSlot6 = 33
flagHiSlot7 = 34

ALSCActionAdd = 6
ALSCActionAssemble = 1
ALSCActionConfigure = 10
ALSCActionEnterPassword = 9
ALSCActionLock = 7
ALSCActionMove = 4
ALSCActionRepackage = 2
ALSCActionSetName = 3
ALSCActionSetPassword = 5
ALSCActionUnlock = 8
ALSCPasswordNeededToLock = 2
ALSCPasswordNeededToOpen = 1
ALSCPasswordNeededToUnlock = 4
ALSCPasswordNeededToViewAuditLog = 8
CTPC_CHAT = 8
CTPC_MAIL = 9
CTPG_CASH = 6
CTPG_SHARES = 7
CTV_ADD = 1
CTV_COMMS = 5
CTV_GIVE = 4
CTV_REMOVE = 2
CTV_SET = 3
SCCPasswordTypeConfig = 2
SCCPasswordTypeGeneral = 1

agentTypeBasicAgent = 2
agentTypeEventMissionAgent = 8
agentTypeGenericStorylineMissionAgent = 6
agentTypeNonAgent = 1
agentTypeResearchAgent = 4
agentTypeStorylineMissionAgent = 7
agentTypeTutorialAgent = 3
agentTypeFactionalWarfareAgent = 9
agentTypeEpicArcAgent = 10
agentTypeAura = 11


agentRangeNearestEnemyCombatZone = 11
agentRangeNeighboringConstellation = 10
agentRangeNeighboringConstellationSameRegion = 9
agentRangeNeighboringSystem = 5
agentRangeNeighboringSystemSameConstellation = 4
agentRangeSameConstellation = 6
agentRangeSameOrNeighboringConstellation = 8
agentRangeSameOrNeighboringConstellationSameRegion = 7
agentRangeSameOrNeighboringSystem = 3
agentRangeSameOrNeighboringSystemSameConstellation = 2
agentRangeSameSystem = 1

agentIskMultiplierLevel1 = 1
agentIskMultiplierLevel2 = 2
agentIskMultiplierLevel3 = 4
agentIskMultiplierLevel4 = 8
agentIskMultiplierLevel5 = 16

agentLpMultiplierLevel1 = 20
agentLpMultiplierLevel2 = 60
agentLpMultiplierLevel3 = 180
agentLpMultiplierLevel4 = 540
agentLpMultiplierLevel5 = 4860

agentLpMultipliers = (agentLpMultiplierLevel1,
 agentLpMultiplierLevel2,
 agentLpMultiplierLevel3,
 agentLpMultiplierLevel4,
 agentLpMultiplierLevel5)


agentIskRandomLowValue  = 11000
agentIskRandomHighValue = 16500

agentIskCapValueLevel1 = 250000
agentIskCapValueLevel2 = 500000
agentIskCapValueLevel3 = 1000000
agentIskCapValueLevel4 = 5000000
agentIskCapValueLevel5 = 9000000

allianceApplicationAccepted = 2
allianceApplicationEffective = 3
allianceApplicationNew = 1
allianceApplicationRejected = 4
allianceCreationCost = 1000000000
allianceMembershipCost = 2000000
allianceRelationshipCompetitor = 3
allianceRelationshipEnemy = 4
allianceRelationshipFriend = 2
allianceRelationshipNAP = 1

attributeAccessDifficulty = 901
attributeAccessDifficultyBonus = 902
attributeAccuracyMultiplier = 205
attributeActivationBlocked = 1349
attributeActivationTargetLoss = 855
attributeAgentAutoPopupRange = 844
attributeAgentCommRange = 841
attributeAgentID = 840
attributeAgility = 70
attributeAimedLaunch = 644
attributeAllowsCloneJumpsWhenActive = 981
attributeAmmoLoaded = 127
attributeAnchoringDelay = 556
attributeAnchoringRequiresSovereignty = 1033
attributeAnchoringRequiresSovereigntyLevel = 1215
attributeAnchoringSecurityLevelMax = 1032
attributeAoeCloudSize = 654
attributeAoeDamageReductionFactor = 1353
attributeAoeDamageReductionSensitivity = 1354
attributeAoeFalloff = 655
attributeAoeVelocity = 653
attributeArmorBonus = 65
attributeArmorDamage = 266
attributeArmorDamageAmount = 84
attributeArmorEmDamageResonance = 267
attributeArmorExplosiveDamageResonance = 268
attributeArmorHP = 265
attributeArmorHPBonusAdd = 1159
attributeArmorHPMultiplier = 148
attributeArmorHpBonus = 335
attributeArmorKineticDamageResonance = 269
attributeArmorThermalDamageResonance = 270
attributeArmorUniformity = 524
attributeAttributePoints = 185
attributeBarrageDmgMultiplier = 326
attributeBaseMaxScanDeviation = 1372
attributeBaseSensorStrength = 1371
attributeBaseScanRange = 1370
attributeBoosterDuration = 330
attributeBoosterness = 1087
attributeBrokenRepairCostMultiplier = 1264
attributeCanCloak = 1163
attributeCanJump = 861
attributeCanNotBeTrainedOnTrial = 1047
attributeCanNotUseStargates = 1254
attributeCanReceiveCloneJumps = 982
attributeCanUseCargoInSpace = 849
attributeCapacitorBonus = 67
attributeCapacitorCapacity = 482
attributeCapacitorCapacityBonus = 1079
attributeCapacitorCapacityMultiplier = 147
attributeCapacitorCharge = 18
attributeCapacitorRechargeRateMultiplier = 144
attributeCapacity = 38
attributeCapacitySecondary = 1233
attributeCapacityBonus = 72
attributeCapRechargeBonus = 314
attributeCaptureProximityRange = 1337
attributeCargoCapacityMultiplier = 149
attributeCargoGroup = 629
attributeCargoScanResistance = 188
attributeCharge = 18
attributeChargeGroup1 = 604
attributeChargeSize = 128
attributeCharisma = 164
attributeCloakingTargetingDelay = 560
attributeCloudDuration = 545
attributeCloudEffectDelay = 544
attributeColor = 1417
attributeConsumptionQuantity = 714
attributeConsumptionType = 713
attributeContrabandDetectionChance = 723
attributeControlTowerMinimumDistance = 1165
attributeCopySpeedPercent = 387
attributeCorporateHangarCapacity = 912
attributeCorporationMemberLimit = 190
attributeCpu = 50
attributeCpuLoad = 49
attributeCpuMultiplier = 202
attributeCpuOutput = 48
attributeCrystalVolatilityChance = 783
attributeCrystalVolatilityDamage = 784
attributeCrystalsGetDamaged = 786
attributeDamage = 3
attributeDamageCloudChance = 522
attributeDamageCloudType = 546
attributeDamageMultiplier = 64
attributeDeadspaceUnsafe = 801
attributeDecloakFieldRange = 651
attributeDecryptorID = 1115
attributeDisallowAssistance = 854
attributeDisallowEarlyDeactivation = 906
attributeDisallowInEmpireSpace = 1074
attributeDisallowOffensiveModifiers = 872
attributeDisallowRepeatingActivation = 1014
attributeDrawback = 1138
attributeDroneBandwidth = 1271
attributeDroneBandwidthLoad = 1273
attributeDroneBandwidthUsed = 1272
attributeDroneCapacity = 283
attributeDroneControlDistance = 458
attributeDroneFocusFire = 1297
attributeDroneIsAggressive = 1275
attributeDroneIsChaotic = 1278
attributeDuplicatingChance = 399
attributeDuration = 73
attributeEcmBurstRange = 142
attributeEmDamage = 114
attributeEmDamageResistanceBonus = 984
attributeEmDamageResonance = 113
attributeEmDamageResonanceMultiplier = 133
attributeEmpFieldRange = 99
attributeEnergyDestabilizationAmount = 97
attributeEntityArmorRepairAmount = 631
attributeEntityAttackDelayMax = 476
attributeEntityAttackDelayMin = 475
attributeEntityAttackRange = 247
attributeEntityBracketColour = 798
attributeEntityChaseMaxDelay = 580
attributeEntityChaseMaxDelayChance = 581
attributeEntityChaseMaxDistance = 665
attributeEntityChaseMaxDuration = 582
attributeEntityChaseMaxDurationChance = 583
attributeEntityCruiseSpeed = 508
attributeEntityDefenderChance = 497
attributeEntityEquipmentGroupMax = 465
attributeEntityEquipmentMax = 457
attributeEntityEquipmentMin = 456
attributeEntityFactionLoss = 562
attributeEntityFlyRange = 416
attributeEntityFlyRangeFactor = 772
attributeEntityGroupRespawnChance = 640
attributeEntityKillBounty = 481
attributeEntityLootCountMax = 251
attributeEntityLootCountMin = 250
attributeEntityLootValueMax = 249
attributeEntityLootValueMin = 248
attributeEntityMaxVelocitySignatureRadiusMultiplier = 1133
attributeEntityMaxWanderRange = 584
attributeEntityMissileTypeID = 507
attributeEntitySecurityMaxGain = 563
attributeEntitySecurityStatusKillBonus = 252
attributeEntityWarpScrambleChance = 504
attributeEvasiveManeuverLevel = 1414
attributeExpiryTime = 1088
attributeExplosionDelay = 281
attributeExplosionDelayWreck = 1162
attributeExplosionRange = 107
attributeExplosiveDamage = 116
attributeExplosiveDamageResistanceBonus = 985
attributeExplosiveDamageResonance = 111
attributeExplosiveDamageResonanceMultiplier = 132
attributeFactionID = 1341
attributeFastTalkPercentage = 359
attributeFighterAttackAndFollow = 1283
attributeFitsToShipType = 1380
attributeGfxBoosterID = 246
attributeGfxTurretID = 245
attributeHarvesterQuality = 710
attributeHasCorporateHangars = 911
attributeHasShipMaintenanceBay = 907
attributeHeatAbsorbtionRateHi = 1182
attributeHeatAbsorbtionRateLow = 1184
attributeHeatAbsorbtionRateMed = 1183
attributeHeatAttenuationHi = 1259
attributeHeatAttenuationLow = 1262
attributeHeatAttenuationMed = 1261
attributeHeatCapacityHi = 1178
attributeHeatCapacityLow = 1200
attributeHeatCapacityMed = 1199
attributeHeatDamage = 1211
attributeHeatDissipationRateHi = 1179
attributeHeatDissipationRateLow = 1198
attributeHeatDissipationRateMed = 1196
attributeHeatGenerationMultiplier = 1224
attributeHeatAbsorbtionRateModifier = 1180
attributeHeatHi = 1175
attributeHeatLow = 1177
attributeHeatMed = 1176
attributeHiSlotModifier = 1374
attributeHiSlots = 14
attributeHitsMissilesOnly = 823
attributeHp = 9
attributeImpactDamage = 660
attributeImplantness = 331
attributeIncapacitationRatio = 156
attributeIntelligence = 165
attributeInventionMEModifier = 1113
attributeInventionMaxRunModifier = 1124
attributeInventionPEModifier = 1114
attributeInventionPropabilityMultiplier = 1112
attributeIsIncapacitated = 1168
attributeIsArcheology = 1331
attributeIsCovert = 1252
attributeIsGlobal = 1207
attributeIsHacking = 1330
attributeIsOnline = 2
attributeIsPlayerOwnable = 589
attributeIsRAMcompatible = 998
attributeJumpClonesLeft = 1336
attributeJumpDriveCapacitorNeed = 898
attributeJumpDriveConsumptionAmount = 868
attributeJumpDriveConsumptionType = 866
attributeJumpDriveDuration = 869
attributeJumpDriveRange = 867
attributeJumpHarmonics = 1253
attributeJumpPortalCapacitorNeed = 1005
attributeJumpPortalConsumptionMassFactor = 1001
attributeJumpPortalDuration = 1002
attributejumpDelayDuration = 1221
attributeKineticDamage = 117
attributeKineticDamageResistanceBonus = 986
attributeKineticDamageResonance = 109
attributeKineticDamageResonanceMultiplier = 131
attributeLauncherGroup = 137
attributeLauncherHardPointModifier = 1369
attributeLauncherSlotsLeft = 101
attributeLeechBalanceFactor = 1232
attributeLootRespawnTime = 470
attributeLowSlotModifier = 1376
attributeLowSlots = 12
attributeManufactureCostMultiplier = 369
attributeManufactureSlotLimit = 196
attributeManufactureTimeMultiplier = 219
attributeManufacturingTimeResearchSpeed = 385
attributeMass = 4
attributeMassAddition = 796 
attributeMaxActiveDrones = 352
attributeMaxDirectionalVelocity = 661
attributeMaxGroupActive = 763
attributeMaxJumpClones = 979
attributeMaxLaborotorySlots = 467
attributeMaxLockedTargets = 192
attributeMaxLockedTargetsBonus = 235
attributeMaxMissileVelocity = 664
attributeMaxOperationalDistance = 715
attributeMaxOperationalUsers = 716
attributeMaxRange = 54
attributeMaxScanDeviation = 788
attributeMaxScanGroups = 1122
attributeMaxShipGroupActive = 910
attributeMaxShipGroupActiveID = 909
attributeMaxStructureDistance = 650
attributeMaxSubSystems = 1367
attributeMaxTargetRange = 76
attributeMaxTargetRangeMultiplier = 237
attributeMaxTractorVelocity = 1045
attributeMaxVelocity = 37
attributeMaxVelocityActivationLimit = 1334
attributeMaxVelocityLimited = 1333
attributeMaxVelocityBonus = 306
attributeMedSlotModifier = 1375
attributeMedSlots = 13
attributeMemory = 166
attributeMetaLevel = 633
attributeMinMissileVelDmgMultiplier = 663
attributeMinScanDeviation = 787
attributeMinTargetVelDmgMultiplier = 662
attributeMineralNeedResearchSpeed = 398
attributeMiningAmount = 77
attributeMiningDroneAmountPercent = 428
attributeMissileDamageMultiplier = 212
attributeMissileEntityAoeCloudSizeMultiplier = 858
attributeMissileEntityAoeFalloffMultiplier = 860
attributeMissileEntityAoeVelocityMultiplier = 859
attributeMissileEntityFlightTimeMultiplier = 646
attributeMissileEntityVelocityMultiplier = 645
attributeMissileNeverDoesDamage = 1075
attributeModifyTargetSpeedChance = 512
attributeModuleReactivationDelay = 669
attributeModuleRepairRate = 1267
attributeMoonAnchorDistance = 711
attributeMoonMiningAmount = 726
attributeNonBrokenModuleRepairCostMultiplier = 1276
attributeNPCAssistancePriority = 1451
attributeNPCAssistanceRange = 1464
attributeNPCRemoteArmorRepairAmount = 1455
attributeNPCRemoteArmorRepairDuration = 1454 
attributeNPCRemoteArmorRepairMaxTargets= 1501
attributeNPCRemoteArmorRepairThreshold = 1456
attributeNPCRemoteShieldBoostAmount = 1460
attributeNPCRemoteShieldBoostDuration = 1458
attributeNPCRemoteShieldBoostMaxTargets = 1502
attributeNPCRemoteShieldBoostThreshold = 1462
attributeOnliningDelay = 677
attributeOnliningRequiresSovereigntyLevel = 1185
attributePosAnchoredPerSolarSystemAmount = 1195
attributePowerTransferAmount = 90
attributeProbeCanScanShips = 1413
attributeOperationalDuration = 719
attributeOptimalSigRadius = 620
attributePackageRadius = 690
attributePerception = 167
attributePlanetAnchorDistance = 865
attributePosCargobayAcceptGroup = 1352
attributePosCargobayAcceptType = 1351
attributePosControlTowerPeriod = 722
attributePosPlayerControlStructure = 1167
attributePosStructureControlAmount = 1174
attributePosStructureControlDistanceMax = 1214
attributePower = 30
attributePowerEngineeringOutputBonus = 313
attributePowerIncrease = 549
attributePowerLoad = 15
attributePowerOutput = 11
attributePowerOutputMultiplier = 145
attributePowerTransferRange = 91
attributePrereqimplant = 641
attributePrimaryAttribute = 180
attributePropulsionFusionStrength = 819
attributePropulsionFusionStrengthBonus = 815
attributePropulsionIonStrength = 820
attributePropulsionIonStrengthBonus = 816
attributePropulsionMagpulseStrength = 821
attributePropulsionMagpulseStrengthBonus = 817
attributePropulsionPlasmaStrength = 822
attributePropulsionPlasmaStrengthBonus = 818
attributeProximityRange = 154
attributeQuantity = 805
attributeRaceID = 195
attributeRadius = 162
attributeRangeFactor = 1373
attributeReactionGroup1 = 842
attributeReactionGroup2 = 843
attributeRechargeRate = 55
attributeRefineryCapacity = 720
attributeRefiningDelayMultiplier = 721
attributeRefiningYieldMultiplier = 717
attributeRefiningYieldPercentage = 378
attributeRepairCostMultiplier = 187
attributeReprocessingSkillType = 790
attributeRequiredSkill1 = 182
attributeRequiredSkill1Level = 277
attributeRequiredSkill2 = 183
attributeRequiredSkill2Level = 278
attributeRequiredSkill3 = 184
attributeRequiredSkill3Level = 279
attributeRequiredSkill4 = 1285
attributeRequiredSkill4Level = 1286
attributeRequiredSkill5 = 1289
attributeRequiredSkill5Level = 1287
attributeRequiredSkill6 = 1290
attributeRequiredSkill6Level = 1288
attributeRequiredThermoDynamicsSkill = 1212
attributeResearchPointCost = 1155
attributeRigSlots = 1137
attributeScanAllStrength = 1136
attributeScanFrequencyResult = 1161

attributeScanGravimetricStrength = 211
attributeScanGravimetricStrengthBonus = 238
attributeScanGravimetricStrengthPercent = 1027
attributeScanLadarStrength = 209
attributeScanLadarStrengthBonus = 239
attributeScanLadarStrengthPercent = 1028
attributeScanMagnetometricStrength = 210
attributeScanMagnetometricStrengthBonus = 240
attributeScanMagnetometricStrengthPercent = 1029
attributeScanRadarStrength = 208
attributeScanRadarStrengthBonus = 241
attributeScanRadarStrengthPercent = 1030

attributeScanRange = 765
attributeScanResolution = 564
attributeScanResolutionBonus = 566
attributeScanResolutionMultiplier = 565
attributeScanSpeed = 79
attributeSecondaryAttribute = 181
attributeShieldBonus = 68
attributeShieldCapacity = 263
attributeShieldCapacityMultiplier = 146
attributeShieldCharge = 264
attributeShieldEmDamageResonance = 271
attributeShieldExplosiveDamageResonance = 272
attributeShieldKineticDamageResonance = 273
attributeShieldRadius = 680
attributeShieldRechargeRate = 479
attributeShieldRechargeRateMultiplier = 134
attributeShieldThermalDamageResonance = 274
attributeShieldUniformity = 484
attributeShipBrokenModuleRepairCostMultiplier = 1277
attributeShipMaintenanceBayCapacity = 908
attributeShipScanResistance = 511
attributeSignatureRadius = 552
attributeSignatureRadiusAdd = 983
attributeSkillLevel = 280
attributeSkillPoints = 276
attributeSkillPointsSaved = 419
attributeSkillTimeConstant = 275
attributeSlots = 47
attributeSmugglingChance = 445
attributeSpawnWithoutGuardsToo = 903
attributeSpecialisationAsteroidGroup = 781
attributeSpecialisationAsteroidYieldMultiplier = 782
attributeSpeedBonus = 80
attributeSpeedFactor = 20 
attributeStationTypeID = 472
attributeStructureBonus = 82
attributeStructureDamageAmount = 83
attributeStructureHPMultiplier = 150
attributeStructureUniformity = 525
attributeSubSystemSlot = 1366
attributeSurveyScanRange = 197
attributeTargetGroup = 189
attributeTargetHostileRange = 143
attributeTargetSwitchDelay = 691
attributeTargetSwitchTimer = 1416
attributeTechLevel = 422
attributeThermalDamage = 118
attributeThermalDamageResistanceBonus = 987
attributeThermalDamageResonance = 110
attributeThermalDamageResonanceMultiplier = 130
attributeTurretHardpointModifier = 1368
attributeTurretSlotsLeft = 102

attributeUnanchoringDelay = 676
attributeUnfitCapCost = 785
attributeUntargetable = 1158
attributeUpgradeCapacity = 1132
attributeUpgradeCost = 1153
attributeUpgradeLoad = 1152
attributeUpgradeSlotsLeft = 1154
attributeUsageWeighting = 862
attributeVolume = 161
attributeVelocityModifier = 1076
attributeWarpBubbleImmune = 1538
attributeWarpCapacitorNeed = 153
attributeWarpScrambleRange = 103
attributeWarpScrambleStatus = 104
attributeWarpSpeedMultiplier = 600
attributeWillpower = 168
attributeDisallowActivateOnWarp = 1245
attributeBaseWarpSpeed = 1281
attributeMaxTargetRangeBonus = 309

attributeRateOfFire = 51

attributeWormholeMassRegeneration = 1384
attributeWormholeMaxJumpMass = 1385
attributeWormholeMaxStableMass = 1383
attributeWormholeMaxStableTime = 1382
attributeWormholeTargetSystemClass = 1381
attributeWormholeTargetDistribution = 1457

effectAnchorDrop = 649
effectAnchorDropForStructures = 1022
effectAnchorLift = 650
effectAnchorLiftForStructures = 1023
effectBarrage = 263
effectBombLaunching = 2971
effectCloaking = 607
effectCloakingWarpSafe = 980
effectCloneVatBay = 2858
effectCynosuralGeneration = 2857
effectConcordWarpScramble = 3713
effectConcordModifyTargetSpeed = 3714
effectConcordTargetJam = 3710
effectDecreaseTargetSpeed = 586
effectDefenderMissileLaunching = 103
effectECMBurst = 53
effectEmpWave = 38
effectEmpWaveGrid = 2071
effectEnergyDestabilizationNew = 2303
effectEntityCapacitorDrain = 1872
effectEntitySensorDampen = 1878
effectEntityTargetJam = 1871
effectEntityTargetPaint = 1879
effectEntityTrackingDisrupt = 1877
effectEwTargetPaint = 1549
effectEwTestEffectWs = 1355
effectEwTestEffectJam = 1358
effectFlagshipmultiRelayEffect = 1495
effectFofMissileLaunching = 104
effectGangBonusSignature = 1411
effectGangShieldBoosterAndTransporterSpeed = 2415
effectGangShieldBoosteAndTransporterCapacitorNeed = 2418
effectGangIceHarvestingDurationBonus = 2441
effectGangInformationWarfareRangeBonus = 2642
effectGangArmorHardening = 1510
effectGangPropulsionJammingBoost = 1546
effectGangShieldHardening = 1548
effectGangECCMfixed = 1648
effectGangArmorRepairCapReducerSelfAndProjected = 3165
effectGangArmorRepairSpeedAmplifierSelfAndProjected = 3167
effectGangMiningLaserAndIceHarvesterAndGasCloudHarvesterMaxRangeBonus = 3296
effectGangGasHarvesterAndIceHarvesterAndMiningLaserDurationBonus = 3302
effectGangGasHarvesterAndIceHarvesterAndMiningLaserCapNeedBonus =3307
effectGangInformationWarfareSuperiority = 3647
effectGangAbMwdFactorBoost = 1755
effectHardPointModifier = 3773
effectHiPower = 12
effectIndustrialCoreEffect = 3492
effectJumpPortalGeneration = 2152
effectJumpPortalGenerationBO = 3674
effectLauncherFitted = 40
effectLeech = 3250
effectLoPower = 11
effectMedPower = 13
effectMineLaying = 102
effectMining = 17
effectMiningClouds = 2726
effectMiningLaser = 67
effectMissileLaunching = 9
effectMissileLaunchingForEntity = 569
effectModifyTargetSpeed2 = 575
effectNPCRemoteArmorRepair = 3852
effectNPCRemoteShieldBoost = 3855
effectOnline = 16
effectOnlineForStructures = 901
effectOpenSpawnContainer = 1738
effectProbeLaunching = 3793
effectProjectileFired = 34
effectProjectileFiredForEntities = 1086
effectRemoteHullRepair = 3041
effectRemoteEcmBurst = 2913
effectRigSlot = 2663
effectSalvaging = 2757
effectScanStrengthBonusTarget = 124
effectscanStrengthTargetPercentBonus = 2246
effectShieldResonanceMultiplyOnline = 105
effectSiegeModeEffect = 3062
effectSkillEffect = 132
effectSlotModifier = 3774
effectSnowBallLaunching = 2413
effectStructureUnanchorForced = 1129
effectSubSystem = 3772
effectSuicideBomb = 885
effectTargetAttack = 10
effectTargetAttackForStructures = 1199
effectTargetGunneryMaxRangeAndTrackingSpeedBonusHostile = 3555
effectTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile = 3690
effectTargetMaxTargetRangeAndScanResolutionBonusHostile = 3584
effectTargetGunneryMaxRangeAndTrackingSpeedBonusAssistance = 3556
effectTargetMaxTargetRangeAndScanResolutionBonusAssistance = 3583
effectTargetPassively = 54
effectTorpedoLaunching = 127
effectTorpedoLaunchingIsOffensive = 2576
effectTractorBeamCan = 2255
effectTriageMode = 3162
effectTurretFitted = 42
effectTurretWeaponRangeFalloffTrackingSpeedMultiplyTargetHostile = 3697
effectUseMissiles = 101
effectWarpDisruptSphere = 3380
effectWarpScramble = 39
effectWarpScrambleForEntity = 563
effectWarpScrambleTargetMWDBlockActivation = 3725
effectModifyShieldResonancePostPercent = 2052
effectModifyArmorResonancePostPercent = 2041
effectModifyHullResonancePostPercent = 3791
effectShipMaxTargetRangeBonusOnline = 3659
effectSensorBoostTargetedHostile = 837
effectmaxTargetRangeBonus = 2646

bloodlineAchura = 11
bloodlineAmarr = 5
bloodlineBrutor = 4
bloodlineCivire = 2
bloodlineDeteis = 1
bloodlineGallente = 7
bloodlineIntaki = 8
bloodlineJinMei = 12
bloodlineKhanid = 13
bloodlineModifier = 10
bloodlineNiKunni = 6
bloodlineSebiestor = 3
bloodlineStatic = 9
bloodlineVherokior = 14

raceAmarr = 4
raceCaldari = 1
raceGallente = 8
raceJove = 16
raceMinmatar = 2

cacheAccRefTypes                        = 102
cacheLogEventTypes                      = 105
cacheMktOrderStates                     = 106
cachePetCategories                      = 107
cachePetQueues                          = 108
cacheChrRaces                           = 111
cacheChrBloodlines                      = 112
cacheChrAncestries                      = 113
cacheChrSchools                         = 114
cacheChrAttributes                      = 115
cacheChrCareers                         = 116
cacheChrSpecialities                    = 117
cacheCrpRegistryGroups                  = 119
cacheCrpRegistryTypes                   = 120
cacheDungeonTriggerTypes                = 121
cacheDungeonEventTypes                  = 122
cacheDungeonEventMessageTypes           = 123
cacheStaOperations                      = 127
cacheCrpActivities                      = 128
cacheDungeonArchetypes                  = 129
cacheTutCriterias                       = 133
cacheTutTutorials                       = 134
cacheTutContextHelp                     = 135
cacheTutCategories                      = 136
cacheSystemEventTypes                   = 138
cacheUserEventTypes                     = 139
cacheUserColumns                        = 140
cacheSystemProcedures                   = 141
cacheStaticSettings                     = 142

cacheChrFactions                        = 201
cacheDungeonDungeons                    = 202
cacheMapSolarSystemJumpIDs              = 203
cacheMapSolarSystemPseudoSecurities     = 204
cacheInvTypeMaterials                   = 205
cacheMapCelestialDescriptions           = 206
cacheGMQueueOrder                       = 207
cacheStaStationUpgradeTypes             = 208
cacheStaStationImprovementTypes         = 209
cacheStaSIDAssemblyLineType             = 210
cacheStaSIDAssemblyLineTypeQuantity     = 211
cacheStaSIDAssemblyLineQuantity         = 212
cacheStaSIDReprocessingEfficiency       = 213
cacheStaSIDOfficeSlots                  = 214
cacheStaSIDServiceMask                  = 215
cacheDogmaTypeAttributes                = 216
cacheDogmaTypeEffects                   = 217
cacheMapRegions                         = 218
cacheMapConstellations                  = 219
cacheMapSolarSystems                    = 220
cacheStaStations                        = 221
cacheMapPlanets                         = 222
cacheRamTypeRequirements                = 223
cacheInvWreckUsage                      = 224
cacheAgentEpicArcs                      = 226
cacheReverseEngineeringTables           = 227
cacheReverseEngineeringTableTypes       = 228
cacheAgentEpicArcJournalData            = 229
cacheAgentEpicMissionMessages           = 230
cacheAgentEpicMissionsStarting          = 231
cacheAgentEpicMissionsBranching         = 232
cacheAgentCorporations                  = 233
cacheAgentCorporationActivities         = 234
cacheAgentEpicMissionsNonEnd            = 235
cacheLocationWormholeClasses            = 236
cacheAgentEpicArcMissions               = 237
cacheAgentEpicArcConnections            = 238

cacheCrpNpcDivisions                    = 303
cacheMapSolarSystemLoadRatios           = 304
cacheStaServices                        = 305
cacheStaOperationServices               = 306

cacheInvCategories                      = 401
cacheInvGroups                          = 402
cacheInvTypes                           = 403
cacheInvBlueprintTypes                  = 404
cacheCrpNpcCorporations                 = 405
cacheAgentAgents                        = 406
cacheDogmaExpressionCategories          = 407
cacheDogmaExpressions                   = 408
cacheDogmaOperands                      = 409
cacheDogmaAttributes                    = 410
cacheDogmaEffects                       = 411
cacheEveMessages                        = 419
cacheEveGraphics                        = 420
cacheMapTypeBalls                       = 421
cacheNpcTypeLoots                       = 423
cacheNpcLootTableFrequencies            = 424
cacheNpcSupplyDemand                    = 425
cacheNpcTypeGroupingClasses             = 427
cacheNpcTypeGroupings                   = 428
cacheNpcTypeGroupingTypes               = 429
cacheNpcTypeGroupingClassSettings       = 430
cacheCrpNpcMembers                      = 431
cacheCrpCorporations                    = 432
cacheAgtContentTemplates                = 433
cacheAgtContentFlowControl              = 434
cacheAgentMissionsKill                  = 435
cacheAgtContentCourierMissions          = 436
cacheAgtContentExchangeOffers           = 437
cacheCrpPlayerCorporationIDs            = 438
cacheEosNpcToNpcStandings               = 439
cacheRamActivities                      = 440
cacheRamAssemblyLineTypes               = 441
cacheRamAssemblyLineTypesCategory       = 442
cacheRamAssemblyLineTypesGroup          = 443
cacheRamInstallationTypes               = 444
cacheRamSkillInfo                       = 445
cacheMktNpcMarketData                   = 446
cacheNpcCommands                        = 447
cacheNpcDirectorCommands                = 448
cacheNpcDirectorCommandParameters       = 449
cacheNpcCommandLocations                = 450
cacheEvePrimeOwners                     = 451
cacheEvePrimeLocations                  = 452
cacheInvTypeReactions                   = 453
cacheAgtPrices                          = 454
cacheAgtResearchStartupData             = 455
cacheAgtOfferDetails                    = 456
cacheAgtStorylineMissions               = 457
cacheAgtOfferTableContents              = 458
cacheFacWarCombatZones                  = 459
cacheFacWarCombatZoneSystems            = 460
cacheAgtContentAgentInteractionMissions = 461
cacheAgtContentTalkToAgentMissions      = 462
cacheAgtContentMissionTutorials         = 463

cacheEspCharacters      = 10002
cacheEspCorporations    = 10003
cacheEspAlliances       = 10004
cacheEspSolarSystems    = 10005
cacheSolarSystemObjects = 10006
cacheCargoContainers    = 10007
cachePriceHistory       = 10008
cacheTutorialVersions   = 10009
cacheSolarSystemOffices = 10010

tableTutorialTutorials = 200001
tableDungeonDungeons   = 300005
tableAgentMissions     = 3000002

corpLogoChangeCost = 100
corpRoleAccountCanQuery1 = 17179869184
corpRoleAccountCanQuery2 = 34359738368
corpRoleAccountCanQuery3 = 68719476736
corpRoleAccountCanQuery4 = 137438953472
corpRoleAccountCanQuery5 = 274877906944
corpRoleAccountCanQuery6 = 549755813888
corpRoleAccountCanQuery7 = 1099511627776
corpRoleAccountCanTake1 = 134217728
corpRoleAccountCanTake2 = 268435456
corpRoleAccountCanTake3 = 536870912
corpRoleAccountCanTake4 = 1073741824
corpRoleAccountCanTake5 = 2147483648
corpRoleAccountCanTake6 = 4294967296
corpRoleAccountCanTake7 = 8589934592
corpRoleAccountant = 256
corpRoleAuditor = 4096
corpRoleCanRentFactorySlot = 1125899906842624
corpRoleCanRentOffice = 562949953421312
corpRoleCanRentResearchSlot = 2251799813685248
corpRoleChatManager = 36028797018963968
corpRoleContainerCanTake1 = 4398046511104
corpRoleContainerCanTake2 = 8796093022208
corpRoleContainerCanTake3 = 17592186044416
corpRoleContainerCanTake4 = 35184372088832
corpRoleContainerCanTake5 = 70368744177664
corpRoleContainerCanTake6 = 140737488355328
corpRoleContainerCanTake7 = 281474976710656
corpRoleContractManager = 72057594037927936
corpRoleStarbaseCaretaker = 288230376151711744
corpRoleDirector = 1
corpRoleEquipmentConfig = 2199023255552
corpRoleFactoryManager = 1024
corpRoleFittingManager = 576460752303423488
corpRoleHangarCanQuery1 = 1048576
corpRoleHangarCanQuery2 = 2097152
corpRoleHangarCanQuery3 = 4194304
corpRoleHangarCanQuery4 = 8388608
corpRoleHangarCanQuery5 = 16777216
corpRoleHangarCanQuery6 = 33554432
corpRoleHangarCanQuery7 = 67108864
corpRoleHangarCanTake1 = 8192
corpRoleHangarCanTake2 = 16384
corpRoleHangarCanTake3 = 32768
corpRoleHangarCanTake4 = 65536
corpRoleHangarCanTake5 = 131072
corpRoleHangarCanTake6 = 262144
corpRoleHangarCanTake7 = 524288
corpRoleJuniorAccountant = 4503599627370496
corpRoleLocationTypeBase = 2
corpRoleLocationTypeHQ = 1
corpRoleLocationTypeOther = 3
corpRolePersonnelManager = 128
corpRoleSecurityOfficer = 512
corpRoleStarbaseConfig = 9007199254740992
corpRoleStationManager = 2048
corpRoleTrader = 18014398509481984
corpRoleInfrastructureTacticalOfficer = 144115188075855872
corpStationMgrGraceMinutes = 60
corpactivityEducation = 18
corpactivityEntertainment = 8
corpactivityMilitary = 5
corpactivitySecurity = 16
corpactivityTrading = 12
corpactivityWarehouse = 10
corpdivisionAccounting = 1
corpdivisionAdministration = 2
corpdivisionAdvisory = 3
corpdivisionArchives = 4
corpdivisionAstrosurveying = 5
corpdivisionCommand = 6
corpdivisionDistribution = 7
corpdivisionFinancial = 8
corpdivisionIntelligence = 9
corpdivisionInternalSecurity = 10
corpdivisionLegal = 11
corpdivisionManufacturing = 12
corpdivisionMarketing = 13
corpdivisionMining = 14
corpdivisionPersonnel = 15
corpdivisionProduction = 16
corpdivisionPublicRelations = 17
corpdivisionSecurity = 19
corpdivisionStorage = 20
corpdivisionSurveillance = 21
corporationStartupCost = 1599800
corporationAdvertisementFlatFee = 500000
corporationAdvertisementDailyRate = 250000

dunArchetypeAgentMissionDungeon = 20
dunArchetypeFacwarDefensive = 32
dunArchetypeFacwarOffensive = 35
dunArchetypeFacwarDungeons = (dunArchetypeFacwarDefensive, dunArchetypeFacwarOffensive)
dunArchetypeWormhole = 38
dunArchetypeZTest = 19
dunEventMessageEnvironment = 3
dunEventMessageImminentDanger = 1
dunEventMessageMissionInstruction = 7
dunEventMessageMissionObjective = 6
dunEventMessageMood = 4
dunEventMessageNPC = 2
dunEventMessageStory = 5
dunEventMessageWarning = 8
dunExpirationDelay = 48
dunTriggerArchaeologyFailure = 16
dunTriggerArchaeologySuccess = 15
dunTriggerArmorConditionLevel = 5
dunTriggerAttacked = 1
dunTriggerEventActivateGate = 1
dunTriggerEventAgentMessage = 23
dunTriggerEventAgentTalkTo = 22
dunTriggerEventDropLoot = 24
dunTriggerEventDungeonCompletion = 11
dunTriggerEventEffectBeaconActivate = 13
dunTriggerEventEffectBeaconDeactivate = 14
dunTriggerEventEntityDespawn = 18
dunTriggerEventEntityExplode = 19
dunTriggerFacWarVictoryPointsGranted = 20
dunTriggerEventMessage = 10
dunTriggerEventMissionCompletion = 9
dunTriggerEventObjectDespawn = 15
dunTriggerEventObjectExplode = 16
dunTriggerEventRangedNPCHealing = 4
dunTriggerEventRangedPlayerDamageEM = 5
dunTriggerEventRangedPlayerDamageExplosive = 6
dunTriggerEventRangedPlayerDamageKinetic = 7
dunTriggerEventRangedPlayerDamageThermal = 8
dunTriggerEventSpawnGuardObject = 3
dunTriggerEventSpawnGuards = 2
dunTriggerExploding = 3
dunTriggerFWProximityEntered = 21
dunTriggerHackingFailure = 12
dunTriggerHackingSuccess = 11
dunTriggerItemPlacedInMissionContainer = 23
dunTriggerMined = 7
dunTriggerProximityEntered = 2
dunTriggerRoomCapturedAlliance = 19
dunTriggerRoomCapturedFacWar = 20
dunTriggerRoomCapturedCorp = 18
dunTriggerRoomEntered = 8
dunTriggerRoomMined = 10
dunTriggerRoomMinedOut = 9
dunTriggerSalvagingFailure = 14
dunTriggerSalvagingSuccess = 13
dunTriggerShieldConditionLevel = 4
dunTriggerShipEnteredBubble = 17
dunTriggerStructureConditionLevel = 6
dungeonGateUnlockPeriod = 66

DUNGEON_ORIGIN_UNDEFINED = None
DUNGEON_ORIGIN_STATIC = 1
DUNGEON_ORIGIN_AGENT = 2
DUNGEON_ORIGIN_PLAYTEST = 3
DUNGEON_ORIGIN_EDIT = 4
DUNGEON_ORIGIN_DISTRIBUTION = 5
DUNGEON_ORIGIN_PATH = 6
DUNGEON_ORIGIN_TUTORIAL = 7

ixItemID = 0
ixTypeID = 1
ixOwnerID = 2
ixLocationID = 3
ixFlag = 4
ixContraband = 5
ixSingleton = 6
ixQuantity = 7
ixGroupID = 8
ixCategoryID = 9
ixCustomInfo = 10

ownerBank = 2
ownerCONCORD = 1000125
ownerNone = 0
ownerSCC = 1000132
ownerStation = 4
ownerSystem = 1
ownerUnknown = 3006
ownerCombatSimulator = 5

locationAbstract = 0
locationSystem = 1
locationBank = 2
locationTemp = 5
locationRecycler = 6
locationTrading = 7
locationGraveyard = 8
locationUniverse = 9
locationHiddenSpace = 9000001
locationJunkyard = 10
locationCorporation = 13
locationSingletonJunkyard = 25
locationTradeSessionJunkyard = 1008
locationCharacterGraveyard = 1501
locationCorporationGraveyard = 1502
locationRAMInstalledItems = 2003
locationAlliance = 3007

minFaction = 500000
maxFaction = 599999
minNPCCorporation = 1000000
maxNPCCorporation = 1999999
minAgent = 3000000
maxAgent = 3999999
minRegion = 10000000
maxRegion = 19999999
minConstellation = 20000000
maxConstellation = 29999999
minSolarSystem = 30000000
maxSolarSystem = 39999999
minValidLocation = 30000000
minValidShipLocation = 30000000
minUniverseCelestial = 40000000
maxUniverseCelestial = 49999999
minStargate = 50000000
maxStargate = 59999999
minStation = 60000000
maxStation = 69999999
minValidCharLocation = 60000000
minUniverseAsteroid = 70000000
maxUniverseAsteroid = 79999999
minPlayerItem = 100000000
maxPlayerItem = 2099999999
minFakeItem = 2100000000
maxNonCapitalModuleSize = 500

factionAmarrEmpire = 500003
factionAmmatar = 500007
factionAngelCartel = 500011
factionCONCORDAssembly = 500006
factionCaldariState = 500001
factionGallenteFederation = 500004
factionGuristasPirates = 500010
factionInterBus = 500013
factionJoveEmpire = 500005
factionKhanidKingdom = 500008
factionMinmatarRepublic = 500002
factionMordusLegion = 500018
factionORE = 500014
factionOuterRingExcavations = 500014
factionSanshasNation = 500019
factionSerpentis = 500020
factionSistersOfEVE = 500016
factionSocietyOfConsciousThought = 500017
factionTheBloodRaiderCovenant = 500012
factionTheServantSistersofEVE = 500016
factionTheSyndicate = 500009
factionThukkerTribe = 500015
factionUnknown = 500021
factionMordusLegionCommand = 500018
factionTheInterBus = 500013
factionAmmatarMandate = 500007
factionTheSociety = 500017

eventCertificateGranted = 231
eventCertificateGrantedGM = 232
eventCertificateRevokedGM = 233
eventDungeonActivategate = 147
eventDungeonCompleteAgent = 146
eventDungeonCompleteDistribution = 176
eventDungeonCompletePathDungeon = 179
eventDungeonEnter = 143
eventDungeonEnterAgent = 144
eventDungeonEnterDistribution = 175
eventDungeonEnterPathDungeon = 178
eventDungeonExpireDistribution = 186
eventDungeonExpirePathDungeon = 180
eventDungeonGivenPathDungeon = 181
eventDungeonSpawnBlockedByOther = 59
eventMissionAccepted = 88
eventMissionAllocationFailure_ItemDeclarationError = 124
eventMissionAllocationFailure_ItemResolutionFailure = 123
eventMissionAllocationFailure_SanityCheckFailure = 122
eventMissionAllocationFailure_UnexpectedException = 125
eventMissionDeclined = 120
eventMissionFailed = 87
eventMissionOfferExpired = 121
eventMissionOfferRemoved = 122
eventMissionOffered = 118
eventMissionQuit = 119
eventMissionSucceeded = 86
eventEpicArcStarted = 243
eventEpicArcCompleted = 244
eventResearchBlueprintAccepted = 106
eventResearchBlueprintOfferExpired = 105
eventResearchBlueprintOfferInvalid = 111
eventResearchBlueprintOfferRejectedIncompatibleAgent = 110
eventResearchBlueprintOfferRejectedInvalidBlueprint = 109
eventResearchBlueprintOfferRejectedRecently = 108
eventResearchBlueprintOfferRejectedTooLowStandings = 107
eventResearchBlueprintOffered = 101
eventResearchBlueprintRejected = 102
eventResearchStarted = 103
eventResearchStopped = 104
eventStandingAgentBuyOff = 71
eventStandingAgentDonation = 72
eventStandingAgentMissionBonus = 80
eventStandingAgentMissionCompleted = 73
eventStandingAgentMissionDeclined = 75
eventStandingAgentMissionFailed = 74
eventStandingAgentMissionOfferExpired = 90
eventStandingCombatAggression = 76
eventStandingCombatAssistance = 112
eventStandingCombatOther = 79
eventStandingCombatPodKill = 78
eventStandingCombatShipKill = 77
eventStandingContrabandTrafficking = 126
eventStandingDecay = 49
eventStandingDerivedModificationNegative = 83
eventStandingDerivedModificationPositive = 82
eventStandingInitialCorpAgent = 52
eventStandingInitialFactionAlly = 70
eventStandingInitialFactionCorp = 54
eventStandingInitialFactionEnemy = 69
eventStandingPirateKillSecurityStatus = 89
eventStandingPlayerCorpSetStanding = 68
eventStandingPlayerSetStanding = 65
eventStandingPropertyDamage = 154
eventStandingReCalcEntityKills = 58
eventStandingReCalcMissionFailure = 61
eventStandingReCalcMissionSuccess = 55
eventStandingReCalcPirateKills = 57
eventStandingReCalcPlayerSetStanding = 67
eventStandingSlashSet = 84
eventStandingStandingreset = 25
eventStandingTutorialAgentInitial = 81
eventStandingUpdatestanding = 45
eventStandingPromotionStandingIncrease = 216
eventStationMoveSystemFull = 234

eventStandingCombatShipKill_OwnFaction = 223
eventStandingCombatPodKill_OwnFaction = 224
eventStandingCombatAggression_OwnFaction = 225
eventStandingCombatAssistance_OwnFaction = 226
eventStandingPropertyDamage_OwnFaction = 227
eventStandingCombatOther_OwnFaction = 228
eventStandingTacticalSiteDefended = 229
eventStandingTacticalSiteConquered = 230

eventStandingRecommendationLetterUsed = 60

eventUnspecifiedAddOffice = 46
eventSlashSetqty = 30
eventSlashSpawn = 28
eventSlashUnspawn = 29
eventUnspecifiedLootgift = 23
eventUnspecifiedContractDelete = 187
eventResearchPointsEdited = 189
eventLPGain = 203
eventLPLoss = 204
eventLPGMChange = 205
eventUnrentOfficeGM = 211
eventUnspecifiedContractMarkFinished = 212

eventCharacterAttributeRespecScheduled = 50
eventCharacterAttributeRespecFree = 51

refSkipLog = -1
refUndefined = 0
refPlayerTrading = 1
refMarketTransaction = 2
refGMCashTransfer = 3
refATMWithdraw = 4
refATMDeposit = 5
refBackwardCompatible = 6
refMissionReward = 7
refCloneActivation = 8
refInheritance = 9
refPlayerDonation = 10
refCorporationPayment = 11
refDockingFee = 12
refOfficeRentalFee = 13
refFactorySlotRentalFee = 14
refRepairBill = 15
refBounty = 16
refBountyPrize = 17
refInsurance = 19
refMissionExpiration = 20
refMissionCompletion = 21
refShares = 22
refCourierMissionEscrow = 23
refMissionCost = 24
refAgentMiscellaneous = 25
refMiscellaneousPaymentToAgent = 26
refAgentLocationServices = 27
refAgentDonation = 28
refAgentSecurityServices = 29
refAgentMissionCollateralPaid = 30
refAgentMissionCollateralRefunded = 31
refAgentMissionReward = 33
refAgentMissionTimeBonusReward = 34
refCSPA = 35
refCSPAOfflineRefund = 36
refCorporationAccountWithdrawal = 37
refCorporationDividendPayment = 38
refCorporationRegistrationFee = 39
refCorporationLogoChangeCost = 40
refReleaseOfImpoundedProperty = 41
refMarketEscrow = 42
refMarketFinePaid = 44
refBrokerfee = 46
refAllianceRegistrationFee = 48
refWarFee = 49
refAllianceMaintainanceFee = 50
refContrabandFine = 51
refCloneTransfer = 52
refAccelerationGateFee = 53
refTransactionTax = 54
refJumpCloneInstallationFee = 55
refManufacturing = 56
refResearchingTechnology = 57
refResearchingTimeProductivity = 58
refResearchingMaterialProductivity = 59
refCopying = 60
refDuplicating = 61
refReverseEngineering = 62
refContractAuctionBid = 63
refContractAuctionBidRefund = 64
refContractCollateral = 65
refContractRewardRefund = 66
refContractAuctionSold = 67
refContractReward = 68
refContractCollateralRefund = 69
refContractCollateralPayout = 70
refContractPrice = 71
refContractBrokersFee = 72
refContractSalesTax = 73
refContractDeposit = 74
refContractDepositSalesTax = 75
refSecureEVETimeCodeExchange = 76
refContractAuctionBidCorp = 77
refContractCollateralCorp = 78
refContractPriceCorp = 79
refContractBrokersFeeCorp = 80
refContractDepositCorp = 81
refContractDepositRefund = 82
refContractRewardAdded = 83
refContractRewardAddedCorp = 84
refBountyPrizes = 85
refCorporationAdvertisementFee = 86
refMedalCreation = 87
refMedalIssuing = 88
refAttributeRespecification = 90
refCombatSimulator = 91

stationServiceBountyMissions        =         1
stationServiceAssassinationMissions =         2
stationServiceCourierMission        =         4
stationServiceInterbus              =         8
stationServiceReprocessingPlant     =        16
stationServiceRefinery              =        32
stationServiceMarket                =        64
stationServiceBlackMarket           =       128
stationServiceStockExchange         =       256
stationServiceCloning               =       512
stationServiceSurgery               =      1024
stationServiceDNATherapy            =      2048
stationServiceRepairFacilities      =      4096
stationServiceFactory               =      8192
stationServiceLaboratory            =     16384
stationServiceGambling              =     32768
stationServiceFitting               =     65536
stationServiceNews                  =    262144
stationServiceStorage               =    524288
stationServiceInsurance             =   1048576
stationServiceDocking               =   2097152
stationServiceOfficeRental          =   4194304
stationServiceJumpCloneFacility     =   8388608
stationServiceLoyaltyPointStore     =  16777216
stationServiceNavyOffices           =  33554432
stationServiceStorefronts           =  67108864
stationServiceCombatSimulator       = 134217728

unitAbsolutePercent = 127
unitAttributeID = 119
unitAttributePoints = 120
unitGroupID = 115
unitInverseAbsolutePercent = 108
unitInversedModifierPercent = 111
unitLength = 1 
unitMass = 2
unitMilliseconds = 101
unitModifierPercent = 109
unitSizeclass = 117
unitTime = 3
unitTypeID = 116
unitVolume = 9
unitCapacitorUnits = 114

billTypeMarketFine = 1
billTypeRentalBill = 2
billTypeBrokerBill = 3
billTypeWarBill = 4
billTypeAllianceMaintainanceBill = 5

chrattrIntelligence = 1
chrattrCharisma = 2
chrattrPerception = 3
chrattrMemory = 4
chrattrWillpower = 5

completedStatusAborted = 2
completedStatusUnanchored = 4
completedStatusDestroyed = 5

ramActivityCopying = 5
ramActivityDuplicating = 6
ramActivityInvention = 8
ramActivityManufacturing = 1
ramActivityNone = 0
ramActivityResearchingMaterialProductivity = 4
ramActivityResearchingTimeProductivity = 3
ramActivityReverseEngineering = 7

ramJobStatusPending = 1
ramJobStatusInProgress = 2
ramJobStatusReady = 3
ramJobStatusDelivered = 4
ramMaxCopyRuns = 20
ramMaxProductionTimeInDays = 30
ramRestrictNone = 0
ramRestrictBySecurity = 1
ramRestrictByStanding = 2
ramRestrictByCorp = 4
ramRestrictByAlliance = 8

activityCopying = 5
activityDuplicating = 6
activityInvention = 8
activityManufacturing = 1
activityNone = 0
activityResearchingMaterialProductivity = 4
activityResearchingTechnology = 2
activityResearchingTimeProductivity = 3
activityReverseEngineering = 7

conAvailPrivate = 1
conAvailPublic = 0

conStatusOutstanding = 0
conStatusInProgress = 1
conStatusFinishedIssuer = 2
conStatusFinishedContractor = 3
conStatusFinished = 4
conStatusCancelled = 5
conStatusRejected = 6
conStatusFailed = 7

conTypeNothing = 0
conTypeItemExchange = 1
conTypeAuction = 2
conTypeCourier = 3
conTypeLoan = 4
conTypeFreeform = 5

facwarCorporationJoining = 0
facwarCorporationActive = 1
facwarCorporationLeaving = 2
facwarStandingPerVictoryPoint = 0.0015
facwarWarningStandingCharacter = 0
facwarWarningStandingCorporation = 1
facwarOccupierVictoryPointBonus = 0.1
facwarStatTypeKill = 0
facwarStatTypeLoss = 1

averageManufacturingCostPerUnitTime = 0
blockAmarrCaldari = 1
blockGallenteMinmatar = 2
blockSmugglingCartel = 3
blockTerrorist = 4
cargoContainerLifetime = 120

containerBank = 10007
containerCharacter = 10011
containerCorpMarket = 10012
containerGlobal = 10002
containerHangar = 10004
containerOffices = 10009
containerRecycler = 10008
containerScrapHeap = 10005
containerSolarSystem = 10003
containerStationCharacters = 10010
containerWallet = 10001
costCloneContract = 5600
costJumpClone = 100000
crpApplicationAcceptedByCharacter = 2
crpApplicationAcceptedByCorporation = 6
crpApplicationAppliedByCharacter = 0
crpApplicationRejectedByCharacter = 3
crpApplicationRejectedByCorporation = 4
crpApplicationRenegotiatedByCharacter = 1
crpApplicationRenegotiatedByCorporation = 5
deftypeCapsule = 670
deftypeHouseWarmingGift = 34
directorConcordSecurityLevelMax = 1000
directorConcordSecurityLevelMin = 450
directorConvoySecurityLevelMin = 450
directorPirateGateSecurityLevelMax = 349
directorPirateGateSecurityLevelMin = -1000
directorPirateSecurityLevelMax = 849
directorPirateSecurityLevelMin = -1000
entityApproaching = 3
entityCombat = 1
entityDeparting = 4
entityDeparting2 = 5
entityEngage = 10
entityFleeing = 7
entityIdle = 0
entityMining = 2
entityOperating = 9
entityPursuit = 6
gangGroupingRange = 300
gangJobCreator = 2
gangJobNone = 0
gangJobScout = 1
gangLeaderRole = 1

gangRoleLeader = 1
gangRoleMember = 4
gangRoleSquadCmdr = 3
gangRoleWingCmdr = 2

gangBoosterNone = 0
gangBoosterFleet = 1
gangBoosterWing = 2
gangBoosterSquad = 3

graphicShipLayerColor0 = 671
graphicShipLayerShape0 = 415
graphicUnknown = 0
invulnerabilityDocking = 3000
invulnerabilityJumping = 5000
invulnerabilityRestoring = 60000
invulnerabilityUndocking = 30000
invulnerabilityWarpingIn = 10000
invulnerabilityWarpingOut = 5000
jumpRadiusFactor = 130
jumpRadiusRandom = 15000
lifetimeOfDefaultContainer = 120
lifetimeOfDurableContainers = 43200
limitCloneJumpHours = 24
lockedContainerAccessTime = 180000
marketCommissionPercentage = 1
maxBoardingDistance = 6550
maxBuildDistance = 10000
maxCargoContainerTransferDistance = 1500
maxConfigureDistance = 5000
maxDockingDistance = 50000
maxDungeonPlacementDistance = 300
maxItemCountPerLocation = 1000
maxJumpInDistance = 13000
maxPetitionsPerDay = 2
maxSelfDestruct = 15000
maxStargateJumpingDistance = 2500
maxWormholeEnterDistance = 5000
maxWarpEndDistance = 100000
maxWarpSpeed = 30
minAutoPilotWarpInDistance = 15000
minDungeonPlacementDistance = 25
minJumpInDistance = 12000
minSpawnContainerDelay = 300000
minWarpDistance = 150000
minWarpEndDistance = 0
mktMinimumFee = 100
mktModificationDelay = 300
mktOrderCancelled = 3
mktOrderExpired = 2
mktTransactionTax = 1
npcCorpMax = 1999999
npcCorpMin = 1000000
npcDivisionAccounting = 1
npcDivisionAdministration = 2
npcDivisionAdvisory = 3
npcDivisionArchives = 4
npcDivisionAstrosurveying = 5
npcDivisionCommand = 6
npcDivisionDistribution = 7
npcDivisionFinancial = 8
npcDivisionIntelligence = 9
npcDivisionInternalSecurity = 10
npcDivisionLegal = 11
npcDivisionManufacturing = 12
npcDivisionMarketing = 13
npcDivisionMining = 14
npcDivisionPersonnel = 15
npcDivisionProduction = 16
npcDivisionPublicRelations = 17
npcDivisionRD = 18
npcDivisionSecurity = 19
npcDivisionStorage = 20
npcDivisionSurveillance = 21
onlineCapacitorChargeRatio = 95
onlineCapacitorRemainderRatio = 33
outlawSecurityStatus = -5
petitionMaxChatLogSize = 200000
petitionMaxCombatLogSize = 200000
posShieldStartLevel = 0.505
posMaxShieldPercentageForWatch = 0.95
posMinDamageDiffToPersist = 0.05
rangeConstellation = 4
rangeRegion = 32767
rangeSolarSystem = 0
rangeStation = -1
rentalPeriodOffice = 30
repairCostPercentage = 100
secLevelForBounty = -1
sentryTargetSwitchDelay = 40000
shipHidingCombatDelay = 120000
shipHidingDelay = 60000
shipHidingPvpCombatDelay = 900000
simulationTimeStep = 1000
skillEventCharCreation = 33
skillEventClonePenalty = 34
skillEventGMGive = 39
skillEventTaskMaster = 35
skillEventTrainingCancelled = 38
skillEventTrainingComplete = 37
skillEventTrainingStarted = 36
skillEventQueueTrainingCompleted = 53
skillEventSkillInjected = 56
skillPointMultiplier = 250
solarsystemTimeout = 86400
starbaseSecurityLimit = 800
terminalExplosionDelay = 30
visibleSubSystems = 5
voteCEO = 0
voteGeneral = 4
voteItemLockdown = 5
voteItemUnlock = 6
voteKickMember = 3
voteShares = 2
voteWar = 1
warRelationshipAtWar = 3
warRelationshipAtWarCanFight = 4
warRelationshipUnknown = 0
warRelationshipYourAlliance = 2
warRelationshipYourCorp = 1
warpJitterRadius = 2500
scanProbeNumberOfRangeSteps = 8
scanProbeBaseNumberOfProbes = 4
solarSystemPolaris = 30000380

leaderboardShipTypeAll = 0
leaderboardShipTypeTopFrigate=1
leaderboardShipTypeTopDestroyer=2
leaderboardShipTypeTopCruiser=3
leaderboardShipTypeTopBattlecruiser=4
leaderboardShipTypeTopBattleship=5

leaderboardPeopleBuddies=1
leaderboardPeopleCorpMembers=2
leaderboardPeopleAllianceMembers=3
leaderboardPeoplePlayersInSim=4

securityClassZeroSec = 0
securityClassLowSec = 1
securityClassHighSec = 2

contestionStateNone = 0
contestionStateContested = 1
contestionStateVulnerable = 2
contestionStateCaptured = 3

aggressionTime = 15

reloadTimer = 10000

dgmAssModAdd = 2
dgmAssModSub = 3
dgmEffActivation = 1
dgmEffArea = 3
dgmEffOnline = 4
dgmEffPassive = 0
dgmEffTarget = 2
dgmTauConstant = 10000

certificateGradeBasic = 1
certificateGradeStandard = 2
certificateGradeImproved = 3
certificateGradeAdvanced = 4
certificateGradeElite = 5

medalMinNameLength        = 3
medalMaxNameLength        = 100
medalMaxDescriptionLength = 1000


respecTimeInterval = 365 * DAY
respecMinimumAttributeValue = 5
respecMaximumAttributeValue = 15
respecTotalRespecPoints = 39

probeStateInactive    = 0
probeStateIdle        = 1
probeStateMoving      = 2
probeStateWarping     = 3
probeStateScanning    = 4
probeStateReturning   = 5

probeResultPerfect = 1.0
probeResultInformative = 0.75
probeResultGood = 0.25
probeResultUnusable = 0.001

# scanner group types
probeScanGroupScrap           = 1
probeScanGroupSignatures      = 4
probeScanGroupShips           = 8
probeScanGroupStructures      = 16
probeScanGroupDronesAndProbes = 32
probeScanGroupCelestials      = 64
probeScanGroupAnomalies       = 128

probeScanGroups = {}
probeScanGroups[probeScanGroupScrap] = set([
    groupBiomass,
    groupCargoContainer,
    groupWreck,
    groupSecureCargoContainer,
    groupAuditLogSecureContainer,
])

probeScanGroups[probeScanGroupSignatures] = set([groupCosmicSignature])

probeScanGroups[probeScanGroupAnomalies] = set([groupCosmicAnomaly])

probeScanGroups[probeScanGroupShips] = set([
    groupAssaultShip,
    groupBattlecruiser,
    groupBattleship,
    groupBlackOps,
    groupCapitalIndustrialShip,
    groupCapsule,
    groupCarrier,
    groupCombatReconShip,
    groupCommandShip,
    groupCovertOps,
    groupCruiser,
    groupDestroyer,
    groupDreadnought,
    groupElectronicAttackShips,
    groupEliteBattleship,
    groupExhumer,
    groupForceReconShip,
    groupFreighter,
    groupFrigate,
    groupHeavyAssaultShip,
    groupHeavyInterdictors,
    groupIndustrial,
    groupIndustrialCommandShip,
    groupInterceptor,
    groupInterdictor,
    groupJumpFreighter,
    groupLogistics,
    groupMarauders,
    groupMiningBarge,
    groupSupercarrier,
    groupRookieship,
    groupShuttle,
    groupStealthBomber,
    groupTitan,
    groupTransportShip,
    groupStrategicCruiser,
])

probeScanGroups[probeScanGroupStructures] = set([
    groupConstructionPlatform,
    groupStationUpgradePlatform,
    groupStationImprovementPlatform,
    groupMobileWarpDisruptor,
    groupAssemblyArray,
    groupControlTower,
    groupCorporateHangarArray,
    groupElectronicWarfareBattery,
    groupEnergyNeutralizingBattery,
    groupForceFieldArray,
    groupJumpPortalArray,
    groupLogisticsArray,
    groupMobileHybridSentry,
    groupMobileLaboratory,
    groupMobileLaserSentry,
    groupMobileMissileSentry,
    groupMobilePowerCore,
    groupMobileProjectileSentry,
    groupMobileReactor,
    groupMobileShieldGenerator,
    groupMobileStorage,
    groupMoonMining,
    groupRefiningArray,
    groupScannerArray,
    groupSensorDampeningBattery,
    groupShieldHardeningArray,
    groupShipMaintenanceArray,
    groupSilo,
    groupStasisWebificationBattery,
    groupStealthEmitterArray,
    groupTrackingArray,
    groupWarpScramblingBattery,
    groupCynosuralSystemJammer,
    groupCynosuralGeneratorArray,
])

probeScanGroups[probeScanGroupDronesAndProbes] = set([
    groupCapDrainDrone,
    groupCombatDrone,
    groupElectronicWarfareDrone,
    groupFighterDrone,
    groupLogisticDrone,
    groupMiningDrone,
    groupProximityDrone,
    groupRepairDrone,
    groupStasisWebifyingDrone,
    groupUnanchoringDrone,
    groupWarpScramblingDrone,
    groupScannerProbe,
    groupSurveyProbe,
    groupWarpDisruptionProbe,
])

probeScanGroups[probeScanGroupCelestials] = set([
    groupAsteroidBelt,
    groupForceField,
    groupMoon,
    groupPlanet,
    groupStargate,
    groupSun,
    groupStation,
])


mapWormholeRegionMin = 11000000
mapWormholeRegionMax = 11999999
mapWormholeConstellationMin = 21000000
mapWormholeConstellationMax = 21999999
mapWormholeSystemMin = 31000000
mapWormholeSystemMax = 31999999

skillQueueTime = 864000000000L
skillQueueMaxSkills = 50

agentMissionOffered = "offered"
agentMissionOfferAccepted = "offer_accepted"
agentMissionOfferDeclined = "offer_declined"
agentMissionOfferExpired = "offer_expired"
agentMissionOfferRemoved = "offer_removed"
agentMissionAccepted = "accepted"
agentMissionDeclined = "declined"
agentMissionCompleted = "completed"
agentMissionQuit = "quit"
agentMissionFailed = "failed"
agentMissionResearchUpdatePPD = "research_update_ppd"
agentMissionResearchStarted = "research_started"
agentMissionProlonged = "prolong"
agentMissionReset = "reset"
agentMissionModified = "modified"

agentMissionStateAllocated = 0
agentMissionStateOffered = 1
agentMissionStateAccepted = 2

rookieAgentList = [
	3018681, 3018821, 3018822, 3018823,
	3018824, 3018680, 3018817, 3018818,
	3018819, 3018820, 3018682, 3018809,
	3018810, 3018811, 3018812, 3018678,
	3018837, 3018838, 3018839, 3018840,
	3018679, 3018841, 3018842, 3018843,
	3018844, 3018677, 3018845, 3018846,
	3018847, 3018848, 3018676, 3018825,
	3018826, 3018827, 3018828, 3018675,
	3018805, 3018806, 3018807, 3018808,
	3018672, 3018801, 3018802, 3018803,
	3018804, 3018684, 3018829, 3018830,
	3018831, 3018832, 3018685, 3018813,
	3018814, 3018815, 3018816, 3018683,
	3018833, 3018834, 3018835, 3018836,
]

petitionPropertyAgentMissionReq = 2
petitionPropertyAgentMissionNoReq = 3
petitionPropertyAgents = 4
petitionPropertyShipID = 5
petitionPropertyStarbaseLocation = 6
petitionPropertyCharacter = 7
petitionPropertyUserCharacters = 8
petitionPropertyWebAddress = 9
petitionPropertyCorporations = 10
petitionPropertyChrAgent = 11
petitionPropertyOS = 12
petitionPropertyChrEpicArc = 13

tutorialPagesActionOpenCareerFunnel = 1

marketCategoryBluePrints = 2
marketCategoryShips = 4
marketCategoryShipEquipment = 9
marketCategoryAmmunitionAndCharges = 11
marketCategoryTradeGoods = 19
marketCategoryImplantesAndBoosters = 24
marketCategorySkills = 150
marketCategoryDrones = 157
marketCategoryManufactureAndResearch = 475
marketCategoryStarBaseStructures = 477
marketCategoryShipModifications = 955

maxCharFittings = 20
maxCorpFittings = 50

dungeonCompletionDestroyLCS = 0
dungeonCompletionDestroyGuards = 1
dungeonCompletionDestroyLCSandGuards = 2

turretModuleGroups = [
 groupEnergyWeapon,
 groupGasCloudHarvester,
 groupHybridWeapon,
 groupMiningLaser,
 groupProjectileWeapon,
 groupStripMiner,
 groupFrequencyMiningLaser,
 groupTractorBeam,
 groupSalvager
]

previewCategories = [
 categoryDrone,
 categoryShip,
 categoryStructure,
 categoryStation,
 categorySovereigntyStructure,
 categoryApparel
]

previewGroups = [
 groupStargate,
 groupFreightContainer,
 groupSecureCargoContainer,
 groupCargoContainer,
 groupAuditLogSecureContainer
] + turretModuleGroups


dgmGroupableGroupIDs = set([
 groupEnergyWeapon,
 groupProjectileWeapon,
 groupHybridWeapon,
 groupMissileLauncher,
 groupMissileLauncherAssault,
 groupMissileLauncherCitadel,
 groupMissileLauncherCruise,
 groupMissileLauncherDefender,
 groupMissileLauncherHeavy,
 groupMissileLauncherHeavyAssault,
 groupMissileLauncherRocket,
 groupMissileLauncherSiege,
 groupMissileLauncherStandard
])

singletonBlueprintOriginal = 1
singletonBlueprintCopy = 2




cacheEosNpcToNpcStandings = 109998
cacheTutContextHelp = 209999
cacheTutCategories = 200006
cacheTutCriterias = 200003
cacheTutTutorials = 200001
cacheTutActions = 200009
cacheDungeonArchetypes = 300001
cacheDungeonDungeons = 300005
cacheDungeonEventMessageTypes = 300017
cacheDungeonEventTypes = 300015
cacheDungeonTriggerTypes = 300013
cacheInvCategories = 600001
cacheInvContrabandTypes = 600008
cacheInvGroups = 600002
cacheInvTypes = 600004
cacheInvTypeMaterials = 600005
cacheInvTypeReactions = 600010
cacheInvWreckUsage = 600009
cacheInvMetaGroups = 600006
cacheInvMetaTypes = 600007
cacheDogmaAttributes = 800004
cacheDogmaEffects = 800005
cacheDogmaExpressionCategories = 800001
cacheDogmaExpressions = 800003
cacheDogmaOperands = 800002
cacheDogmaTypeAttributes = 800006
cacheDogmaTypeEffects = 800007
cacheDogmaUnits = 800009
cacheEveMessages = 1000001
cacheInvBlueprintTypes = 1200001
cacheMapRegions = 1409999
cacheMapConstellations = 1409998
cacheMapSolarSystems = 1409997
cacheMapSolarSystemLoadRatios = 1409996
cacheLocationWormholeClasses = 1409994
cacheMapPlanets = 1409993
cacheMapSolarSystemJumpIDs = 1409992
cacheMapSolarSystemPseudoSecurities = 1409991
cacheMapTypeBalls = 1400001
cacheMapCelestialDescriptions = 1400008
cacheMapLocationScenes = 1400006
cacheMapLocationWormholeClasses = 1400002
cacheMapRegionsTable = 1400009
cacheMapConstellationsTable = 1400010
cacheMapSolarSystemsTable = 1400011
cacheNpcCommandLocations = 1600009
cacheNpcCommands = 1600005
cacheNpcDirectorCommandParameters = 1600007
cacheNpcDirectorCommands = 1600006
cacheNpcLootTableFrequencies = 1600004
cacheNpcTypeGroupingClassSettings = 1600016
cacheNpcTypeGroupingClasses = 1600015
cacheNpcTypeGroupingTypes = 1600017
cacheNpcTypeGroupings = 1600014
cacheNpcTypeLoots = 1600001
cacheRamSkillInfo = 1809999
cacheRamActivities = 1800003
cacheRamAssemblyLineTypes = 1800006
cacheRamAssemblyLineTypesCategory = 1800004
cacheRamAssemblyLineTypesGroup = 1800005
cacheRamCompletedStatuses = 1800007
cacheRamInstallationTypes = 1800002
cacheRamTypeRequirements = 1800001
cacheReverseEngineeringTableTypes = 1800009
cacheReverseEngineeringTables = 1800008
cacheShipInsurancePrices = 2000007
cacheShipTypes = 2000001
cacheStaOperations = 2209999
cacheStaServices = 2209998
cacheStaOperationServices = 2209997
cacheStaSIDAssemblyLineQuantity = 2209996
cacheStaSIDAssemblyLineType = 2209995
cacheStaSIDAssemblyLineTypeQuantity = 2209994
cacheStaSIDOfficeSlots = 2209993
cacheStaSIDReprocessingEfficiency = 2209992
cacheStaSIDServiceMask = 2209991
cacheStaStationImprovementTypes = 2209990
cacheStaStationUpgradeTypes = 2209989
cacheStaStations = 2209988
cacheMktOrderStates = 2409999
cacheMktNpcMarketData = 2400001
cacheCrpRoles = 2809999
cacheCrpActivities = 2809998
cacheCrpNpcDivisions = 2809997
cacheCrpCorporations = 2809996
cacheCrpNpcMembers = 2809994
cacheCrpPlayerCorporationIDs = 2809993
cacheCrpTickerNamesStatic = 2809992
cacheNpcSupplyDemand = 2800001
cacheCrpRegistryGroups = 2800002
cacheCrpRegistryTypes = 2800003
cacheCrpNpcCorporations = 2800006
cacheAgentAgents = 3009999
cacheAgentCorporationActivities = 3009998
cacheAgentCorporations = 3009997
cacheAgentEpicMissionMessages = 3009996
cacheAgentEpicMissionsBranching = 3009995
cacheAgentEpicMissionsNonEnd = 3009994
cacheAgtContentAgentInteractionMissions = 3009992
cacheAgtContentFlowControl = 3009991
cacheAgtContentTalkToAgentMissions = 3009990
cacheAgtPrices = 3009989
cacheAgtResearchStartupData = 3009988
cacheAgtContentTemplates = 3000001
cacheAgentMissionsKill = 3000006
cacheAgtStorylineMissions = 3000008
cacheAgtContentCourierMissions = 3000003
cacheAgtContentExchangeOffers = 3000005
cacheAgentEpicArcConnections = 3000013
cacheAgentEpicArcMissions = 3000015
cacheAgentEpicArcs = 3000012
cacheAgtContentMissionExtraStandings = 3000020
cacheAgtContentMissionTutorials = 3000018
cacheAgtContentMissionLocationFilters = 3000021
cacheAgtOfferDetails = 3000004
cacheAgtOfferTableContents = 3000010
cacheChrSchools = 3209997
cacheChrRaces = 3200001
cacheChrBloodlines = 3200002
cacheChrAncestries = 3200003
cacheChrCareers = 3200004
cacheChrSpecialities = 3200005
cacheChrBloodlineNames = 3200010
cacheChrAttributes = 3200014
cacheChrFactions = 3200015
cacheChrDefaultOverviews = 3200011
cacheChrDefaultOverviewGroups = 3200012
cacheChrNpcCharacters = 3200016
cacheFacWarCombatZoneSystems = 4500006
cacheFacWarCombatZones = 4500005
cacheActBillTypes = 6400004
cachePetCategories = 8109999
cachePetQueues = 8109998
cachePetCategoriesVisible = 8109997
cacheGMQueueOrder = 8109996
cacheCertificates = 5100001
cacheCertificateRelationships = 5100004
cachePlanetSchematics = 7300004
cachePlanetSchematicsTypeMap = 7300005
cachePlanetSchematicsPinMap = 7300003
cacheBattleStatuses = 100509999
cacheBattleResults = 100509998
cacheBattleServerStatuses = 100509997
cacheBattleMachines = 100509996
cacheBattleClusters = 100509995
cacheMapDistrictCelestials = 100309999
cacheMapDistricts = 100300014
cacheMapBattlefields = 100300015
cacheMapLevels = 100300020
cacheMapOutposts = 100300022

cacheResGraphics = 2001800001
cacheResSounds = 2001800002
cacheResIcons = 2001800004

cacheEspCorporations = 1
cacheEspAlliances = 2
cacheEspSolarSystems = 3
cacheSolarSystemObjects = 4
cacheCargoContainers = 5
cachePriceHistory = 6
cacheTutorialVersions = 7
cacheSolarSystemOffices = 8

DBTYPE_I2 = 2
DBTYPE_I4 = 3
DBTYPE_R8 = 5
DBTYPE_WSTR = 130
